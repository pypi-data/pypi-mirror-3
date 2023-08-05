Introduction
============

``repoze.who.plugins.cas`` is a plugin for the `repoze.who framework
<http://static.repoze.org/whodocs/>`_
enabling straightforward "cassification" (i.e.: makings each of your
applications part of the SSO mechanism) of all applications that can be deployed
through `Python Paste <http://pythonpaste.org/deploy/>`_.

It currently supports CAS 3.0, although it may be used with others versions of CAS (yet, no compatibility is ensured as it has only been tested with CAS 3.0).

Applications which can be used :

- App complying with the `simple_authentication WSGI specification <http://wsgi.org/wsgi/Specifications/simple_authentication>`_, which take advantage of the REMOTE_USER key in the WSGI environment.
- App which can handle themselves the CAS mechanism (e.g.: phpBB with the CAS patch, - use wphp as a paste filter for integration of PHP with python - )

Links :

- `Official link for CAS <http://www.jasig.org/cas>`_

.. contents::

Credits
======================================
|makinacom|_

* `Planet Makina Corpus <http://www.makina-corpus.org>`_
* `Contact us <mailto:python@makina-corpus.org>`_

.. |makinacom| image:: http://depot.makina-corpus.org/public/logo.gif
.. _makinacom:  http://www.makina-corpus.com


