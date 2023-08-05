Introduction
============

This product is done *only* for Plone 3. It backports the Plone 4 **related contents** viewlet to old
Plone 3 versions. Do not install this on Plone 4. Really.

You could need this package if and only if you have a product that you want to be compatible with
Plone 3 and Plone 4, keeping the content's view template at the Plone 4 style.

Product details
===============

One of the most problematic change done in Plone 4 is the removal of related contents area from
common views, replaced with a more flexible viewlet.

Commonly every Plone 3 contents view contains a part of code like this::

    ...
    <div metal:use-macro="here/document_relateditems/macros/relatedItems">
       show related items if they exist
    </div>
    ...

Removing this code and transform this as a viewlet has been a great change. However this is a problem for
developers that still take care of Plone 3 compatibility:

* If we keep the "Plone 3 style" template (as above) we will see a *doubled related contents* area on
  Plone 4.
* If we remove the related contents part from our template, we won't see related contents in Plone 3
  (so we removed part of our compatibility).

But we can do better. This product gives to Plone a related items viewlet (as Plone 4 do) compatible
with Plone 3, keeping Plone 3 CSS styles.

What you need is to update your template to Plone 4 layout (removing the explicit related items area) but
make it compatible with this product.

Guide for 3rd party products
----------------------------

If you want to fix a 3rd party product that is already using the Plone 4 related items style, so you don't
see related anymore when using it on Plone 3, you simply need fix your buildout:

* add ``collective.relateditems`` to you eggs
* add to a .zcml this piece of code (explicitly in one of yours packages, or using `zcml-additional`__)::

      <include package="collective.relateditems" />
      <class class="your.product.content.YourContentClass">
          <implements interface="collective.relateditems.interfaces.IRelatedItemsEnabledContent"/>
      </class>

__ http://pypi.python.org/pypi/plone.recipe.zope2instance#advanced-zcml-options

Note that you don't need to change anything inside the 3rd party code.

Guide for products you own
--------------------------

If you are a product developer and you want to make your product fully compatible with Plone 4 but also
Plone 3, your can also choose to hide to your users all configuration difficulties.
You need to change something in your code.

First of all, you need to make your product based on ``collective.relateditems`` only when you are in a
Plone 3 environment. The common way is to check the Python version in your ``setup.py``::

    >>> import os, sys
    ...
    >>> install_requires = ['setuptools',
    ...                     'Products.CMFPlone',
    ...                     # other dependencies
    ...                     ]
    ...
    >>> if sys.version_info < (2, 6):
    ...     install_requires.append('collective.relateditems')

Then the product definition::

   >>> setup(name='your.product',
   ...     # more
   ...     install_requires=install_requires,
   ...     #more
   ... )

After that you need to proper define your ``configure.zcml``::

    <configure zcml:condition="installed collective.relateditems">
        <include package="collective.relateditems" />
	    <class class="your.product.content.YourContentClass">
            <implements interface="collective.relateditems.interfaces.IRelatedItemsEnabledContent"/>
        </class>
    </configure>

You can also make your ``YourContentClass`` Python class implementing the ``IRelatedItemsEnabledContent`` but
you still need to remember that Plone 4 environment will not have this interface available.

That's all.
