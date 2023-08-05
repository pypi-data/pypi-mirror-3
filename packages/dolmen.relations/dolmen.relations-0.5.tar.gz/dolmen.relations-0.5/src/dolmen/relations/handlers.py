# -*- coding: utf-8 -*-

import grokcore.component as grok

from dolmen.relations import events, ICatalog, IRelationValue
from zope.component import getUtility, adapter, queryUtility
from zope.event import notify
from zope.intid.interfaces import IIntIds, IIntIdRemovedEvent


@grok.subscribe(IRelationValue, events.IRelationModifiedEvent)
def update_relation(relation, event):
    intids = getUtility(IIntIds)
    catalog = getUtility(ICatalog)
    catalog.unindex(relation)
    catalog.index_doc(intids.getId(relation), relation)


@grok.subscribe(IRelationValue, events.IRelationAddedEvent)
def add_relation(relation, event):
    """We index the relation then mark the source and target with
    the correct marker, to be sure it will trigger the events later.
    """
    intids = getUtility(IIntIds)
    catalog = getUtility(ICatalog)
    catalog.index_doc(intids.register(relation), relation)


@adapter(IIntIdRemovedEvent)
def object_deleted(event):

    ob = event.object
    catalog = queryUtility(ICatalog)
    if catalog is None:
        # We don't have a Catalog installed in this part of the site
        return

    if IRelationValue.providedBy(ob):
        # We assume relations can't be source or targets of relations
        catalog.unindex(ob)
        return

    intids = getUtility(IIntIds, context=ob)
    uid = intids.queryId(ob)
    if uid is None:
        return

    rels = list(catalog.findRelations({'source_id': uid}))
    for rel in rels:
        notify(events.RelationSourceDeletedEvent(ob, rel))
        parent = rel.__parent__
        try:
            del parent[rel.__name__]
        except KeyError:
            continue

    rels = list(catalog.findRelations({'target_id': uid}))
    for rel in rels:
        notify(events.RelationTargetDeletedEvent(ob, rel))
        parent = rel.__parent__
        try:
            del parent[rel.__name__]
        except KeyError, e:
            continue
