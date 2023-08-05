##############################################################################
#
# Copyright (c) 2005 Zope Corporation. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Visible Source
# License, Version 1.0 (ZVSL).  A copy of the ZVSL should accompany this
# distribution.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""objectlog implementation

$Id: log.py 9482 2006-04-28 04:44:31Z gary $
"""
import pytz, datetime, persistent, transaction
from BTrees import IOBTree
import zope.security.management
import zope.security.interfaces
import zope.security.checker
import zope.security.proxy
from zope import interface, schema, event
import zope.interface.interfaces
import zope.location
import zope.app.keyreference.interfaces

from zc.objectlog import interfaces, utils
from zc.objectlog.i18n import _

def performDeferredLogs(deferred, seen, transaction):
    # deferred is dict of 
    # (parent key reference, log name): (not if_changed list, if_changed list)
    # where not if_changed and if_changed are both lists of
    # [(log, summary, details)]
    problem = False
    for hook, args, kwargs in reversed(
        tuple(transaction.getBeforeCommitHooks())):
        if hook is performDeferredLogs:
            break
        else:
            if (hook, args, kwargs) not in seen:
                seen.append((hook, args, kwargs))
                problem = True
    if problem:
        transaction.addBeforeCommitHook(
            performDeferredLogs, (deferred, seen, transaction))
    else:
        for always, if_changed in deferred.values():
            if always:
                for log, summary, details in always:
                    log._call(summary, details)
            else:
                log, summary, details = if_changed[0]
                log._call(summary, details, if_changed=True)

def getTransactionFromPersistentObject(obj):
    # this should maybe go in ZODB; extracted from some of Jim's code
    connection = obj._p_jar
    if connection is None:
        return False
    try:
        tm = connection._txn_mgr
    except AttributeError:
        tm = connection.transaction_manager
    return tm.get()

class Log(persistent.Persistent, zope.location.Location):
    interface.implements(interfaces.ILog)

    def __init__(self, record_schema):
        self.entries = IOBTree.IOBTree()
        self._record_schema = record_schema

    def record_schema(self, value):
        if self.entries:
            last_schema = self[-1].record_schema
            if value is not last_schema and not value.extends(last_schema):
                raise ValueError(
                    _("Once entries have been made, may only change schema to "
                      "one that extends the last-used schema"))
        self._record_schema = value
    record_schema = property(lambda self: self._record_schema, record_schema)

    def __call__(self, 
                 summary=None, details=None, defer=False, if_changed=False):
        if defer:
            o = self.__parent__
            key = (zope.app.keyreference.interfaces.IKeyReference(o),
                   self.__name__)
            t = getTransactionFromPersistentObject(self) or transaction.get()
            # the following approach behaves badly in the presence of
            # savepoints.  TODO: convert to use persistent data structure that
            # will be rolled back when a savepoint is rolled back.
            for hook, args, kwargs in t.getBeforeCommitHooks():
                if hook is performDeferredLogs:
                    deferred = args[0]
                    ds = deferred.get(key)
                    if ds is None:
                        ds = deferred[key] = ([], [])
                    break
            else:
                ds = ([], [])
                deferred = {key: ds}
                t.addBeforeCommitHook(performDeferredLogs, (deferred, [], t))
            ds[bool(if_changed)].append((self, summary, details))
        else:
            return self._call(summary, details, if_changed=if_changed)

    def _call(self, summary, details, if_changed=False):
        s = self.record_schema
        new_record = s(self.__parent__)
        utils.validate(new_record, s)
        entries_len = len(self)
        changes = {}
        if entries_len:
            old_record = self[-1].record
            for name, field in schema.getFieldsInOrder(s):
                old_val = field.query(old_record, field.missing_value)
                new_val = field.query(new_record, field.missing_value)
                if new_val != old_val:
                    changes[name] = new_val
        else:
            for name, field in schema.getFieldsInOrder(s):
                changes[name] = field.query(new_record, field.missing_value)
        if not if_changed or changes:
            new = LogEntry(
                entries_len, changes, self.record_schema, summary, details)
            zope.location.locate(new, self, unicode(entries_len))
            utils.validate(new, interfaces.ILogEntry)
            self.entries[entries_len] = new
            event.notify(interfaces.LogEntryEvent(self.__parent__, new))
            return new
        # else return None

    def __getitem__(self, ix):
        if isinstance(ix, slice):
            indices = ix.indices(len(self))
            return [self.entries[i] for i in range(*indices)]
        # XXX put this in traversal adapter (I think)
        if isinstance(ix, basestring):
            ix = int(ix)
        if ix < 0:
            ix = len(self) + ix
        try:
            return self.entries[ix]
        except KeyError:
            raise IndexError, 'list index out of range'
    
    def __len__(self):
        if self.entries:
            return self.entries.maxKey() + 1
        else:
            return 0

    def __iter__(self):
        for l in self.entries.values():
            yield l

class LogEntry(persistent.Persistent, zope.location.Location):
    interface.implements(interfaces.ILogEntry)

    def __init__(self, ix, record_changes, record_schema, 
                 summary, details):
        self.index = ix
        self.record_changes = utils.ImmutableDict(record_changes)
        self.record_schema = record_schema
        self.summary = summary
        self.details = details
        self.timestamp = datetime.datetime.now(pytz.utc)
        try:
            interaction = zope.security.management.getInteraction()
        except zope.security.interfaces.NoInteraction:
            self.principal_ids = ()
        else:
            self.principal_ids = tuple(
                [unicode(p.principal.id) for p in interaction.participations
                 if zope.publisher.interfaces.IRequest.providedBy(p)])
    
    record = property(lambda self: Record(self))

    def next(self):
        try:
            return self.__parent__[self.index+1]
        except IndexError:
            return None
    next = property(next)
    
    def previous(self):
        ix = self.index
        if ix:
            return self.__parent__[ix-1]
        else: # it's 0
            return None
    previous = property(previous)

class RecordChecker(object):
    interface.implements(zope.security.interfaces.IChecker)

    def check_setattr(self, obj, name):
        raise zope.security.interfaces.ForbiddenAttribute, (name, obj)

    def check(self, obj, name):
        if name not in zope.security.checker._available_by_default:
            entry = zope.security.proxy.removeSecurityProxy(obj.__parent__)
            schema = entry.record_schema
            if name not in schema:
                raise zope.security.interfaces.ForbiddenAttribute, (name, obj)
    check_getattr = __setitem__ = check

    def proxy(self, value):
        'See IChecker'
        checker = getattr(value, '__Security_checker__', None)
        if checker is None:
            checker = zope.security.checker.selectChecker(value)
            if checker is None:
                return value
        return zope.security.checker.Proxy(value, checker)

class Record(zope.location.Location): # not intended to be persistent
    interface.implements(interfaces.IRecord)
    
    __name__ = u"record"
    
    __Security_checker__ = RecordChecker()
    
    def __init__(self, entry):
        self.__parent__ = entry
        interface.directlyProvides(self, entry.record_schema)

    def __getattr__(self, name):
        entry = self.__parent__
        schema = entry.record_schema
        try:
            field = schema[name]
        except KeyError:
            raise AttributeError, name
        else:
            while entry is not None:
                if name in entry.record_changes:
                    v = value = entry.record_changes[name]
                    break
                entry = entry.previous
            else: # we currently can never get here
                v = value = getattr(schema[name], 'missing_value', None)
            if zope.interface.interfaces.IMethod.providedBy(field):
                v = lambda : value
            setattr(self, name, v)
            return v
