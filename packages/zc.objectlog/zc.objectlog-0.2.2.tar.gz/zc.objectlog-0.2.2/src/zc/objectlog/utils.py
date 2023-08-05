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
"""utilities for the objectlog module

$Id: utils.py 12198 2006-06-14 20:56:25Z gary $
"""
from zope import interface, schema
import zope.interface.common.mapping
from zope.schema.interfaces import RequiredMissing

def validate(obj, i): # XXX put this in zope.schema?
    i.validateInvariants(obj)
    for name, field in schema.getFieldsInOrder(i):
        value = field.query(obj, field.missing_value)
        if value == field.missing_value:
            if field.required:
                raise RequiredMissing(name)
        else:
            bound = field.bind(obj)
            bound.validate(value)

# !!! The ImmutableDict class is from an unreleased ZPL package called aimles,
# included for distribution here with the author's (Gary Poster) permission
class ImmutableDict(dict):
    """A dictionary that cannot be mutated (without resorting to superclass
    tricks, as shown below).
    
      >>> d = ImmutableDict({'name':'Gary', 'age':33})
      >>> d['name']
      'Gary'
      >>> d['age']
      33
      >>> d.get('foo')
      >>> d.get('name')
      'Gary'
      >>> d['name'] = 'Karyn'
      Traceback (most recent call last):
      ...
      RuntimeError: Immutable dictionary
      >>> d.clear()
      Traceback (most recent call last):
      ...
      RuntimeError: Immutable dictionary
      >>> d.update({'answer':42})
      Traceback (most recent call last):
      ...
      RuntimeError: Immutable dictionary
      >>> del d['name']
      Traceback (most recent call last):
      ...
      RuntimeError: Immutable dictionary
      >>> d.setdefault('sense')
      Traceback (most recent call last):
      ...
      RuntimeError: Immutable dictionary
      >>> d.pop('name')
      Traceback (most recent call last):
      ...
      RuntimeError: Immutable dictionary
      >>> d.popitem()
      Traceback (most recent call last):
      ...
      RuntimeError: Immutable dictionary
      >>> d2 = ImmutableDict.fromkeys((1,2,3))
      >>> type(d2.copy()) # copy is standard mutable dict
      <type 'dict'>
      >>> import pprint
      >>> pprint.pprint(d2.copy()) # pprint gets confused by subtypes
      {1: None, 2: None, 3: None}
      >>> pprint.pprint(ImmutableDict.fromkeys((1,2,3),'foo'))
      {1: 'foo', 2: 'foo', 3: 'foo'}
    
    Here's an example of actually mutating the dictionary anyway.
    
      >>> dict.__setitem__(d, 'age', 33*12 + 7)
      >>> d['age']
      403

    pickling and unpickling is supported.
    
      >>> import pickle
      >>> copy = pickle.loads(pickle.dumps(d))
      >>> copy is d
      False
      >>> copy == d
      True

      >>> import cPickle
      >>> copy = cPickle.loads(cPickle.dumps(d))
      >>> copy is d
      False
      >>> copy == d
      True
    """
    interface.implements(
        zope.interface.common.mapping.IExtendedReadMapping,
        zope.interface.common.mapping.IClonableMapping)
    def __setitem__(self, key, val):
        raise RuntimeError('Immutable dictionary')
    def clear(self):
        raise RuntimeError('Immutable dictionary')
    def update(self, other):
        raise RuntimeError('Immutable dictionary')
    def __delitem__(self, key):
        raise RuntimeError('Immutable dictionary')
    def setdefault(self, key, failobj=None):
        raise RuntimeError('Immutable dictionary')
    def pop(self, key, *args):
        raise RuntimeError('Immutable dictionary')
    def popitem(self):
        raise RuntimeError('Immutable dictionary')
    @classmethod
    def fromkeys(cls, iterable, value=None):
        return cls(dict.fromkeys(iterable, value))

