Introduction
============

This addon add a "baseline" to the header of Plone. By default it display the
website description property but you can use use a dedicated property in 
the Plone registry ('collective.baseline' key).

template configuration
======================

By default the class used to render the baseline use the site description.
It will try to load the value of portal_registry with the 'collective.baseline'
key.

You can override this template using z3c.job / plone.app.themingplugins using
following variables:

* view/site_url
* view/portal_state
* view/navigation_root_url
* view/site_title
* view/site_desc
* view/baseline

Credits
=======

Companies
---------

|makinacom|_

* `Planet Makina Corpus <http://www.makina-corpus.org>`_
* `Contact Makina Corpus <mailto:python@makina-corpus.org>`_

Authors
-------

- JeanMichel FRANCOIS aka toutpt <toutpt@gmail.com>

.. Contributors

.. |makinacom| image:: http://depot.makina-corpus.org/public/logo.gif
.. _makinacom:  http://www.makina-corpus.com
