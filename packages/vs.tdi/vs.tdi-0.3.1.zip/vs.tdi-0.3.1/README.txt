vs.tdi  - Tabbed document interface for Plone 4
-----------------------------------------------

vs.tdi provides a supplementary views for folderish object (implementing
IATFolder).  The new view provides a tabbed interface for accessing content
inside the folder (supported content-types: Document, NewsItem, Event). The
standard ``tdi_view`` retrieves all HTML to be rendered with one HTTP request.
The ``tdi_ajax_view`` performs an ajax request upon each tab change.

Requirements
============
- Plone 4

Installation
============
The standard Plone installation procedure applies (add ``vs.tdi`` to your
buildout configuration, re-run buildout and add install it within your Plone site).

Licence
=======
vs.tdi is published under the GNU Public Licence V2 (GPL 2)

Authors
=======

| Andreas Jung
| ZOPYX Ltd.
| info@zopyx.com
| www.zopyx.com
|
| Veit Schiele
| Veit Schiele communications GmbH
| kontakt@veit-schiele.de
| www.veit-schiele.de

