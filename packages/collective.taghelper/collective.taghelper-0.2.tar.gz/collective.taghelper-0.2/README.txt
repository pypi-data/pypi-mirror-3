Project Description
===================

Taghelper uses OpenCalais, Yahoo, SiLLC and tagthe.net

Installation with buildout
==========================

Add collective.taghelper to the eggs section of you buildout: ::

    eggs =
        collective.taghelper


Activate the product in your add ons section. This will install a Tag Helper
controlpanel in you site setup. You have to fill in the API Keys for the
webservices you want to use and choose if you want to use the local content
or the destination of a link if your content type has an attribute remote_url
(In Plone OOTB this would be the link type). The product adds
a new tab for your content named tagging. In this form you can choose the
keywords you want to add to your content. Keywords assigned earlier
manually will be preserved.

- Code repository: https://svn.plone.org/svn/collective/collective.taghelper/
- Questions and comments to product-developers@lists.plone.org
- Report bugs at http://plone.org/products/collective.taghelper/issues

