.. contents::

Introduction
============

This is an additional set of **column types** for `DatagridField`__ product for Plone.

__ http://plone.org/products/datagridfield

New columns
===========

TextAreaColumn
--------------

Like the base *Column* type, just display a ``textarea`` HTML element.

Additional parameters:

``rows``
    Default: 3. Number of rows of the textarea.
``cols``
    Default: 0. Number of columns of the textarea. If not provided the
    html ``cols`` attribute is omitted and an inline style "*width: 100%*"
    wil be used instead.

Example::

    ...
    DataGridField('foo',
              columns=("type", "description"),
              widget = DataGridWidget(
                        columns={
                             'type' : Column(_(u"Type")),
                             'description' : TextAreaColumn(_(u"Description"),
                                                            rows=10,
                                                            cols=20),
                        },
             ),
    ),
    ...

SelectColumn
------------

Like the default *SelectColumn* from DataGridField product, but explicitly support the
``vocabulary_factory`` way to provide vocabularies.

Additional parameters:

``vocabulary_factory``
    Provide the name of a registered vocabulary using a Zope Component Utility. See the
    Archetypes Develop Manual for more.
``vocabulary``
    As default SelectColumn, required only if you don't provide ``vocabulary_factory``.
    Use this to call a method on the context to obtain the vocabulary.

Example::

    ...
    DataGridField('foo',
              columns=("type", "description"),
              widget = DataGridWidget(
                        columns={
                             'type' : SelectColumn(_(u"Type"),
                                                   vocabulary_factory='plone.app.vocabularies.PortalTypes'),
                             'description' : Column(_(u"Description"),),
                        },
             ),
    ),
    ...

**Note**: the base *SelectColumn* of DataGridField 1.8 already have some kind of support for Zope-3-like vocabularies,
however the use of it is not clean (and *this* version also works on Plone 3).

ReferenceColumn
---------------

This is a complex column type that store an unique object "*UID*". The default view rendering of this column
will display a proper link to the referenced object.

You can use this is different ways. In the simpler example, just use it as a textual column::

    ...
    DataGridField('foo',
              columns=("uid", "comment"),
              widget = DataGridWidget(
                        columns={
                             'uid' : ReferenceColumn(_(u"Reference")),
                             'comment' : Column(_(u"Comment")),
                        },
             ),
    ),
    ...

So you are on your own to store a propert UID in the field (not very interesting, isn't it?).

If you want something more, you can enable an additional JavaScript module and you'll get an
**autocomplete feature** of referenced objects::

    ...
    DataGridField('foo',
              columns=("uid", "comment"),
              widget = DataGridWidget(
                        helper_js= ('datagridwidget.js', 'datagridautocomplete.js'),
                        columns={
                             'uid' : ReferenceColumn(_(u"Reference")),
                             'comment' : Column(_(u"Comment")),
                        },
             ),
    ),
    ...

So you will add to the default ``datagridwidget.js`` (automatically provided by the widget) a new
``datagridautocomplete.js`` ones.

When using autocomplete text field, you can query Plone in two different way:

* starting a query with the "``/``" character will query documents by *path*, so you can manually
  surf the whole site.
* starting as query with other character will perform a full-text query on titles.

This will required `jQueryUI autocomplete`__. Please, read also the "Dependencies" section below.

__ http://jqueryui.com/demos/autocomplete/

Additional parameters:

``object_provides``
    When using the full-text query, only return results of objects that provide those interfaces.
    Default is an empty list (no filter).

Dependencies
============

This product has been tested on *Plone 3.3* and *DataGridField 1.6*. Tests and feedback with
Plone 4 and DataGridField 1.8 are welcome!

jQueryUI
--------

A column above need that Plone provide jQueryUI library. This product *will not* cover this
requirement, even by dependency.

If you have already jQueryUI autocomplete behaviour in your Plone site, you are already ok.

If you need it, take a look at `collective.jqueryui.autocomplete`__ (or read it's documentation page
to understand how cover this need).

__ http://plone.org/products/collective.jqueryui.autocomplete

Authors
=======

This product was developed by RedTurtle Technology team.

.. image:: http://www.redturtle.it/redturtle_banner.png
   :alt: RedTurtle Technology Site
   :target: http://www.redturtle.it/

Contribute!
-----------

You are *welcome* to help us, contributing and adding new columns!

Credits
=======

Developed with the support of `Regione Emilia Romagna`__; Regione Emilia Romagna supports
the `PloneGov initiative`__.

__ http://www.regione.emilia-romagna.it/
__ http://www.plonegov.it/
