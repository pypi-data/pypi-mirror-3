================
dolmen.relations
================

`dolmen.relations` is a thin layer above `zc.relation`, allowing a
simple and straightforward implementation of standalone relationships
between objects.

Getting started
===============

In order to demonstrate the package's features, we first set up a sane
environment::

  >>> from zope import component
  >>> from zope.container.btree import BTreeContainer

  >>> sm = component.getGlobalSiteManager()
  >>> herd = getRootFolder()['herd'] = BTreeContainer()


Relations catalog
-----------------

`dolmen.relations` provides a component called `RelationCatalog` that
is in charge of registering the relations and finding them::

  >>> from dolmen.relations import RelationCatalog, ICatalog
  >>> sm.registerUtility(RelationCatalog(), ICatalog)


Relations container
-------------------

To store the relations and trigger the needed events,
`dolmen.relations` provides a btree container::
 
  >>> from dolmen.relations import RelationsContainer
  >>> relations = herd['_relations'] = RelationsContainer()


Content
-------

Now, we need some content to get started. The tests module defines a
Mammoth persistent object that we are going to use here::

  >>> from dolmen.relations.tests import Mammoth
 
  >>> manfred = herd['manfred'] = Mammoth()
  >>> gunther = herd['gunther'] = Mammoth()

To be sure that our objects will be persisted and will be
granted an int id, we commit::

  >>> import transaction
  >>> transaction.commit()


Relations
=========

The relations proposed by `dolmen.relations` are of the "A to B"
type. They allow you to link a source object with a target object. For
tests purposes, we are going to create two Mammoth objects that are
going to be used as source and target::

  >>> from dolmen.relations import values, any
  >>> from zope.intid.interfaces import IIntIds
  >>> ids = component.getUtility(IIntIds)
  >>> rcatalog = component.getUtility(ICatalog)

  >>> gunther_id = ids.getId(gunther)
  >>> manfred_id = ids.getId(manfred)


Simple relation
---------------

The first and simpliest relation type is the `RelationValue`. This
relation is created with a source id and target id::

  >>> relations["simple"] = values.RelationValue(gunther_id, manfred_id)
  
You can query the relations by giving the target and/or source id::

  >>> found = list(rcatalog.findRelations({'target_id': manfred_id}))
  >>> found
  [<dolmen.relations.values.RelationValue object at ...>]

The relation has attributes dedicated to resolving the source or
target::

  >>> relation = found.pop()
  >>> relation
  <dolmen.relations.values.RelationValue object at ...>
  >>> relation.source
  <Mammoth gunther>
  >>> relation.target
  <Mammoth manfred>


Tagged relation
---------------

The second type of relation is the `TaggedRelationValue`. It allows us to
add to the a source-target couple, a list of tags as a list of
unicode strings::

  >>> relations["tagged"] = values.TaggedRelationValue(
  ...           gunther_id, manfred_id, tags=[u'grok', u'dolmen'])

The relation can still be retrieved with a basic query::

  >>> found = list(rcatalog.findRelations({'target_id': manfred_id}))
  >>> found
  [<dolmen.relations.values.RelationValue object at ...>, <dolmen.relations.values.TaggedRelationValue object at ...>]

It can also, now, be queried using a tag value::

  >>> found = list(rcatalog.findRelations({'tag': any('grok')}))
  >>> found
  [<dolmen.relations.values.TaggedRelationValue object at ...>]

  >>> found = list(rcatalog.findRelations({'tag': any('drupal')}))
  >>> found
  []


Stateful relation
-----------------

The third type of relation is the `StatefulRelationValue`. It adds, to
the source-target couple, state information as a unicode string::

  >>> relations["stateful"] = values.StatefulRelationValue(
  ...           gunther_id, manfred_id, state=u"private")

The relation can still be retrieved with a basic query::

  >>> found = list(rcatalog.findRelations({'target_id': manfred_id}))
  >>> found
  [<dolmen.relations.values.RelationValue object at ...>, <dolmen.relations.values.TaggedRelationValue object at ...>, <dolmen.relations.values.StatefulRelationValue object at ...>]

It can also, now, be queried using the state string::

  >>> found = list(rcatalog.findRelations({'state': any('private')}))
  >>> found
  [<dolmen.relations.values.StatefulRelationValue object at ...>]

  >>> found = list(rcatalog.findRelations({'state': any('public')}))
  >>> found
  []


Events
======

Whenever an object is deleted, the relations using it as source or
target are deleted also::

  >>> del herd['manfred']
  >>> print list(herd['_relations'].keys())
  []
  >>> found = list(rcatalog.findRelations({'target_id': manfred_id}))
  >>> found
  []
