# -*- coding: utf-8 -*-

import BTrees
from zc.relation.catalog import Catalog
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from dolmen.relations.interfaces import *


def dump(obj, catalog, cache):
    intids = cache.get('intids')
    if intids is None:
        intids = cache['intids'] = getUtility(IIntIds)
    return intids.register(obj)


def load(token, catalog, cache):
    intids = cache.get('intids')
    if intids is None:
        intids = cache['intids'] = getUtility(IIntIds)
    return intids.getObject(token)


class RelationCatalog(Catalog):

    def __init__(self):
        """Create the relation catalog with indexes.
        """
        Catalog.__init__(self, dump, load)

        self.addValueIndex(
            IRelationValue['source_id'])

        self.addValueIndex(
            IRelationValue['target_id'])

        self.addValueIndex(
            IStatefulRelationValue['state'],
            btree = BTrees.family32.OI)

        self.addValueIndex(
            ITaggedRelationValue['tags'],
            btree=BTrees.family32.OO,
            multiple=True,
            name='tag')
