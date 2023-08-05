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
"""objectlog package interfaces

$Id: interfaces.py 9482 2006-04-28 04:44:31Z gary $
"""
from zope import interface, schema
import zope.interface.common.sequence
import zope.interface.common.mapping
import zope.component.interfaces

from i18n import _

class ILog(zope.interface.common.sequence.IFiniteSequence):
    def __call__(summary=None, details=None, defer=False, if_changed=False):
        """add an ILogEntry to logged with optional details, summary, and data.

        details should be a schema.Text field; summary should be a
        schema.TextLine field.  The details and summary fields will move to
        rich text fields when they are available.

        Adapts self.__parent__ to self.record_schema, checks the adapted value
        to see if it validates with the schema, compares the current
        values with the last logged values, and creates a log entry with the
        change set, the current record_schema, the summary, the details, and
        the data.

        If defer is True, will defer making the log entry until the end of the
        transaction (a non-guaranteed point within the transaction's
        beforeCommitHooks, but before other subsequent deferred log calls).

        If if_changed is True, a log will only be made if a change has been
        made since the last log entry.

        If both defer and if_changed are True, any other log entries that are
        deferred but not if_changed will come first, effectively eliminating
        all deferred, if_changed entries.  Similarly, if there are no deferred,
        non-if_changed entries, only the first requested if_changed log will
        be made.
        """

    record_schema = schema.InterfaceField(
        title=_("Record Schema"),
        description=_("""The schema used for creating log entry records.

        May be altered with a schema that extends the last-used schema.

        Non-schema specifications (e.g., interface.Attribute and methods) are
        ignored.
        """),
        required=True)

class ILogging(interface.Interface):
    "An object which provides an ILog as a 'log' attribute"

    log = schema.Object(ILog, title=_('Log'), description=_(
                        "A zc.objectlog.ILog"), readonly=True, required=True)

class IRecord(interface.Interface):
    """Data about the logged object when the log entry was made.

    Records always implement an additional interface: the record_schema of the
    corresponding log entry."""

class ILogEntry(interface.Interface):
    """A log entry.

    Log entries have three broad use cases:
    - Record transition change messages from system users
    - Record basic status values so approximate change timestamps can
      be calculated
    - Allow for simple extensibility.
    """
    timestamp = schema.Datetime(
        title=_("Creation Date"),
        description=_("The date and time at which this log entry was made"),
        required=True, readonly=True)

    principal_ids = schema.Tuple(
        value_type=schema.TextLine(),
        title=_("Principals"),
        description=_(
            """The ids of the principals who triggered this log entry"""),
        required=True, readonly=True)

    summary = schema.TextLine( # XXX Make rich text line later
        title=_("Summary"),
        description=_("Log summary"),
        required=False, readonly=True)

    details = schema.Text( # XXX Make rich text later
        title=_("Details"),
        description=_("Log details"),
        required=False, readonly=True)

    record_schema = schema.InterfaceField(
        title=_("Record Schema"),
        description=_("""The schema used for creating log entry records.

        Non-schema specifications (e.g., interface.Attribute and methods) are
        ignored."""),
        required=True, readonly=True)

    record_changes = schema.Object(
        zope.interface.common.mapping.IExtendedReadMapping,
        title=_("Changes"),
        description=_("Changes to the object since the last log entry"),
        required=True, readonly=True)

    record = schema.Object(
        IRecord,
        title=_("Full Status"),
        description=_("The status of the object at this log entry"),
        required=True, readonly=True)

    next = interface.Attribute("The next log entry, or None if last")

    previous = interface.Attribute("The previous log entry, or None if first")

class IAggregatedLog(interface.Interface):
    """an iterable of logs aggregated for a given object"""

class ILogEntryEvent(zope.component.interfaces.IObjectEvent):
    """object is log's context (__parent__)"""

    entry = interface.Attribute('the log entry created')

class LogEntryEvent(zope.component.interfaces.ObjectEvent):
    interface.implements(ILogEntryEvent)
    def __init__(self, obj, entry):
        super(LogEntryEvent, self).__init__(obj)
        self.entry = entry
