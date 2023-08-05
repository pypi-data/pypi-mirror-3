# -*- coding: utf-8 -*-

from zope.component.interfaces import ObjectEvent, IObjectEvent
from zope.lifecycleevent.interfaces import (
    IObjectAddedEvent, IObjectRemovedEvent)
from zope.lifecycleevent import ObjectAddedEvent, ObjectRemovedEvent
from zope.interface import implements, Attribute


class IRelationAddedEvent(IObjectAddedEvent):
    """A relation has been added.
    """


class IRelationDeletedEvent(IObjectEvent):
    """A relation has been deleted.
    """


class IRelationModifiedEvent(IObjectRemovedEvent):
    """A relation has been modified.
    """

class IRelationSourceDeletedEvent(IObjectEvent):
    """The source of a relation has been deleted.
    """
    relation = Attribute(u"Relation")


class IRelationTargetDeletedEvent(IObjectEvent):
    """The target of a relation has been deleted.
    """
    relation = Attribute(u"Relation")


class RelationAddedEvent(ObjectAddedEvent):
    implements(IRelationAddedEvent)


class RelationDeletedEvent(ObjectRemovedEvent):
    implements(IRelationDeletedEvent)


class RelationModifiedEvent(ObjectEvent):
    implements(IRelationModifiedEvent)


class RelationSourceDeletedEvent(ObjectEvent):
    implements(IRelationSourceDeletedEvent)

    def __init__(self, object, relation):
        self.object = object
        self.relation = relation


class RelationTargetDeletedEvent(ObjectEvent):
    implements(IRelationTargetDeletedEvent)

    def __init__(self, object, relation):
        self.object = object
        self.relation = relation
