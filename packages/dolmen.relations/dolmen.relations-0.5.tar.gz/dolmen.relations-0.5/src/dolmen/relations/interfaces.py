# -*- coding: utf-8 -*-

from zope.schema import Int, TextLine, List
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface, Attribute
from zope.container.interfaces import IContainer
from zope.container.constraints import contains

_ = MessageFactory('dolmen.relations')


class IRelationsContainer(IContainer):
    """A container to store relations.
    """
    contains('.IRelationValue')


class IRelationValue(Interface):
    """A simple relation One to One.
    """
    source_id = Int(
        title = _(u"source_intid", default=u"Intid of the source object"),
        required = True,
        )

    target_id = Int(
        title = _(u"target_intid", default=u"Intid of the target object"),
        required = True,
        )

    source = Attribute("The source object of the relation.")
    target = Attribute("The target object of the relation.")


class IStatefulRelationValue(IRelationValue):
    """A relation with a state.
    """
    state = TextLine(
        title = _(u"state", default=u"State of the relation"),
        required = True,
        default = u""
        )


class ITaggedRelationValue(IRelationValue):
    """A relation that handles tags.
    """
    tags = List(
        title = _(u"tags", default=u"Tags of the relation"),
        required = True,
        default = [],
        value_type = TextLine()
        )


__all__ = ("IRelationsContainer", "IRelationValue",
           "IStatefulRelationValue", "ITaggedRelationValue")
