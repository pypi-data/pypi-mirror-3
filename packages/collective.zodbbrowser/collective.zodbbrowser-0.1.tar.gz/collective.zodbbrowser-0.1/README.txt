============
Introduction
============

Collective.ZodbBrowser is a web application to browse, inspect and introspect Zope's zodb objects. It is inspired on smalltalk's class browser and zodbbrowsers for zope3. 

There is a demo video available at `YouTube's menttes channel
<http://www.youtube.com/watch?v=GkOpdnC5zvs/>`_. 

====================================
Using ZodbBrowser with your buildout
====================================

If you already have a buildout for Plone3 or Plone4 running, edit 
buildout.cfg to add collective.zodbbrowser to eggs and zcml sections at buildout
and instance parts respectively.

::

  [buildout]
  ...
  eggs = collective.zodbbrowser
  ...

Autoinclude is automatically configured to work in Plone but if you are using 
any other systems, make sure to add a zcml slug::

  ...
  [instance]
  ...
  zcml = collective.zodbbrowser

Then run bin/buildout to make the changes effective.



