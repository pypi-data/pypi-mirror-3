vs.jquerybookmarks
------------------

Integration of the jquery.bookmark plugin
http://keith-wood.name/bookmark.html

Requirements
============
- Plone 4.X

Installation
============
The standard Plone installation procedure applies (add ``vs.jquerybookmarks`` to your
buildout configuration, re-run buildout and add install it within your Plone site).

Customizing
===========
Out of the box ``vs.jquerybookmarks`` will display icons for all available
services. The suggested approach to tailor down the services to your needs is
to override/customize ``vs.jquerybookmarks/vs/jquerybooks/browser/viewlet.pt``
template using ``z3c.jbot`` inside your own policy package. Due to the huge
number of supported services and formating options there will not be a
through-the-web configuration option.

Code
====
- https://github.com/zopyx/vs.jquerybookmarks

Issue tracker
=============
- https://github.com/zopyx/vs.jquerybookmarks/issues


Licence
=======
vs.jquerybookmarks is published under the GNU Public Licence V2 (GPL 2)

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

