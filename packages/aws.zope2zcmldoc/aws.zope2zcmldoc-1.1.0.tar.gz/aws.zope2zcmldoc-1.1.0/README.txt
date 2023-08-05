================
aws.zope2zcmldoc
================

An additional Zope 2 control panel that renders the live ZCML documentation,
this means the ZCML that is installed in your Zope instance, including the ZCML
vocabulary provided by the third party components. Read more details and have a
look at some screenshots in `this blog post
<http://glenfant.wordpress.com/2011/04/20/zcml-wadda-want-a-live-zcml-doc/>`_.

Intended audience
=================

This component is clearly dedicated to Zope developers and integrators. This
component does not provide features for the end user.

Works with
==========

``aws.zope2zcmldoc`` has been tested with Zope 2.10 to Zope 2.13. It may or may
not work with earlier or later versions of Zope.

Tests reports with other Zope versions, and related contributions are welcome
(note that supporting Zope 2.8 and earlier versions is not considered).

Installation
============

With ``zc.buildout`` and ``plone.recipe.zope2instance``, you just need to add
this in your ``buildout.cfg`` file ::

  ...
  [instance]
  recipe = plone.recipe.zope2instance
  ...
  eggs =
      ...
      aws.zope2zcmldoc
      ...
  # You don't need this if you have Plone 3.3 or later in the eggs list
  zcml =
      ...
      aws.zope2zcmldoc
      ...


.. admonition:: Control panel creation

   Sorry for the impatients but I did not find the way to automate the creation
   of a new Zope 2 control panel at Zope startup. In order to complete the
   installation, and install the control panel entry, open a browser in your
   Zope root as Manager and type in your address bar:

   ``http://<your-zope-root>/@@install-aws-zope2zcmldoc``

Now go to the Zope Control Panel and learn the various ZCML namespaces, elements
and attributes.

Uninstallation
==============

Before removing the ``aws.zope2zcmldoc`` from your ``buildout.cfg`` and
rebuilding your instance, you may want to remove the control panel entry.

Removing the Control Panel entry is not essential, but if you don't do this, a
slate entry will be left in the Zope Control Panel of your Zope instance.

Start your Zope instance, open a browser in your Zope root as Manager and type
in your address bar:

   ``http://<your-zope-root>/@@uninstall-aws-zope2zcmldoc``

License
=======

This software is licensed under GNU GPL available here:
http://www.gnu.org/licenses/gpl.html

Some URLs
=========

On Pypi:
   http://pypi.python.org/pypi/aws.zope2zcmldoc

Subversion repository:
   https://svn.plone.org/svn/collective/aws.zope2zcmldoc/

Contributors
============

* `Gilles Lenfant <gilles.lenfant@-NO-SPAM-alterway.fr>`_: Main developer.

* `Leonardo Caballero <leonardocaballero@-NO-SPAM-gmail.com>`_: i18n and spanish
  translations.

Sponsored by Alter Way
======================

http://www.alterway.fr
