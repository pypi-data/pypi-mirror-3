import os.path
import unittest

from zope.testing import doctest
from zope.app.testing import functional

from ZODB.interfaces import IConnection
from persistent import Persistent
from persistent.interfaces import IPersistent
from zope import component
from zope.intid import IntIds
from zope.intid.interfaces import IIntIds
from zope.container.contained import Contained
from zope.keyreference.persistent import KeyReferenceToPersistent
from zope.keyreference.persistent import connectionOfPersistent
from zope.keyreference.interfaces import IKeyReference

ftesting_zcml = os.path.join(os.path.dirname(__file__), 'ftesting.zcml')
FunctionalLayer = functional.ZCMLLayer(
    ftesting_zcml, __name__, 'FunctionalLayer',allow_teardown=True)


class Mammoth(Contained, Persistent):
    def __repr__(self):
        return "<Mammoth %s>" % self.__name__


class RelationTestSetup(functional.FunctionalTestSetup):
    """A setup with an IntId utility registered
    """
    def setUp(self):
        functional.FunctionalTestSetup.setUp(self)
        base = component.getGlobalSiteManager()
        base.registerUtility(IntIds(), IIntIds)
        base.registerAdapter(
            connectionOfPersistent, (IPersistent,), IConnection)
        base.registerAdapter(
            KeyReferenceToPersistent, (IPersistent,), IKeyReference)


def setUp(test):
    RelationTestSetup().setUp()

def tearDown(test):
    RelationTestSetup().tearDown()


def test_suite():
    """Testing suite.
    """
    readme = functional.FunctionalDocFileSuite(
        'README.txt', setUp = setUp, tearDown = tearDown,
        optionflags=(doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE),
        )

    readme.layer = FunctionalLayer
    suite = unittest.TestSuite()
    suite.addTest(readme)
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
