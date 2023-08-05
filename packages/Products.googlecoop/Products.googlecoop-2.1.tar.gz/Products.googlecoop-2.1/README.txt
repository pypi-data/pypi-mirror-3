Introduction
============
Google Co-op 2.0 is a complete rewrite of Google Co-op for plone 4.
It was built using paster. It does not add any new content types to your
site, just an additional view for plone collections and plone site.

Install
=======

Add ``Products.googlecoop`` to the list of eggs to install, e.g.: ::

    [buildout]
    ...
    eggs =
        ...
        Products.googlecoop

Re-run buildout, e.g. with: ::

    $ ./bin/buildout


Install the Product in Site-Setup Add/Remove Products. Enter your
Custom Search Engine's unique identifier in the googlecoop configuration.
(You find the identifier in the code section in the control panel of
your searchengine)

You can access the search page of your search engine by adding
/@@googlecoop_view to the url of your plone instance.

Options
=======

In the Google Co-op control panel you can customize almost any aspect
of your custom search engine


Create a Linked Custom Search Engine using a Collection
=======================================================

After the installation of the product a new view 'Google CSE View'
is available for collections. In a Linked CSE the specification of the
search engine is hosted on your website. Google retrieves the CSE
specification from your website when your user searches in the CSE.
The specifications can be accessed by adding @@cseannotations.xml and
@@csecontext.xml to your plone site root or a collection.

This has several very important benefits:

* You can easily convert the results of a topic to a Custom Search Engine.
* You can automatically generate any number of CSEs.
* You can easily update your Linked CSE definitions without pushing data to Google.
* There are no global, per user annotation limits.

You can now exploit the full power of your ideas to dynamically generate CSEs.

Links
=====

- Code repository: https://svn.plone.org/svn/collective/Products.googlecoop/
- Questions and comments to product-developers@lists.plone.org
- Report bugs at http://plone.org/products/google-co-op/issues


