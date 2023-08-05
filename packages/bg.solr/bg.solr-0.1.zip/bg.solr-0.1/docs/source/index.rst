Introduction
============

``bg.solr`` is a Solr web-frontend integrated with Plone 3/4
for querying a Solr instance filled with content from ``bg.crawler``.

Requirements
============

* Solr 3.X
* Plone 3 oder Plone 4

Installation
============

* added ``bg.solr`` to the eggs option of your buildout.cfg and
  re-run buildout.

Usage
============

* add ``/@@solr-search`` to the root URL of your Plone site in order
  to see the search form (http://host:port/path/to/plone/@@solr-search).


Sourcecode
==========

https://github.com/zopyx/bg.solr


Bug tracker
===========

https://github.com/zopyx/bg.solr/issues

Solr setup
==========

You can use the buildout configuration from

https://raw.github.com/zopyx/bg.crawler/master/solr-3.4.cfg

as an example how to setup a Solr instance for using
``bg.crawler``.


Licence
=======

``bg.solr`` is published under the GNU Public Licence V2 (GPL 2)

Credits
=======

``bg.solr`` is sponsored by BG Phoenics

Author
======

| ZOPYX Ltd.
| Charlottenstr. 37/1
| D-72070 Tuebingen
| Germany
| info@zopyx.com
| www.zopyx.com

