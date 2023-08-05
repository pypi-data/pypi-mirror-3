# -*- coding: utf-8 -*-

from persistent import Persistent
from dolmen.relations.interfaces import *

from zope.component import getUtility
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty
from zope.intid.interfaces import IIntIds
from zope.container.contained import Contained


class RelationValue(Contained, Persistent):
    implements(IRelationValue)
    source_id = FieldProperty(IRelationValue['source_id'])
    target_id = FieldProperty(IRelationValue['target_id'])

    def __init__(self, source_id, target_id):
        self.source_id = source_id
        self.target_id = target_id

    def __resolve(self, content_id):
        try:
            resolver = self._v_resolver
        except AttributeError:
            resolver = self._v_resolver = getUtility(IIntIds).queryObject
        try:
            return resolver(content_id)
        except KeyError:
            return None

    @property
    def source(self):
        return self.__resolve(self.source_id)

    @property
    def target(self):
        return self.__resolve(self.target_id)


class StatefulRelationValue(RelationValue):
    implements(IStatefulRelationValue)
    state = FieldProperty(IStatefulRelationValue['state'])

    def __init__(self, source_id, target_id, state=u""):
        RelationValue.__init__(self, source_id, target_id)
        self.state = state


class TaggedRelationValue(RelationValue):
    implements(ITaggedRelationValue)
    tags = FieldProperty(ITaggedRelationValue['tags'])

    def __init__(self, source_id, target_id, tags=[]):
        RelationValue.__init__(self, source_id, target_id)
        self.tags = tags


__all__ = ['RelationValue',
           'StatefulRelationValue',
           'TaggedRelationValue']
