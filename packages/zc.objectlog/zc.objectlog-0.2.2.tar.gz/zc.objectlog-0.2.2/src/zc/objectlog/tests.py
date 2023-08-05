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
"""objectlog module test runner

$Id: tests.py 12198 2006-06-14 20:56:25Z gary $
"""

import unittest, transaction
from zope.testing import doctest, module
from zope.testing.doctestunit import DocTestSuite
from zope.component import testing

def setUp(test):
    testing.setUp(test)
    module.setUp(test, 'zc.objectlog.log_txt')

def tearDown(test):
    module.tearDown(test)
    testing.tearDown(test)
    transaction.abort()
    db = test.globs.get('db')
    if db is not None:
        db.close()

def copierSetUp(test):
    testing.setUp(test)
    import zope.security.management
    import zope.security.interfaces
    import zope.app.security.interfaces
    from zope import interface, schema
    import zope.component
    import zope.publisher.interfaces
    class DummyPrincipal(object):
        interface.implements(zope.security.interfaces.IPrincipal)
        def __init__(self, id, title, description):
            self.id = unicode(id)
            self.title = title
            self.description = description
    
    alice = DummyPrincipal('alice', 'Alice Aal', 'a principled principal')
    class DummyParticipation(object):
        interface.implements(zope.publisher.interfaces.IRequest)
        interaction = principal = None
        def __init__(self, principal):
            self.principal = principal
    zope.security.management.newInteraction(DummyParticipation(alice))
    module.setUp(test, 'zc.objectlog.copier_txt')

def copierTearDown(test):
    import zope.security.management
    zope.security.management.endInteraction()
    module.tearDown(test)
    testing.tearDown(test)

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('log.txt',
                             setUp=setUp, tearDown=tearDown,),
        doctest.DocFileSuite('copier.txt',
                             setUp=copierSetUp, tearDown=copierTearDown,),
        DocTestSuite('zc.objectlog.utils'),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
