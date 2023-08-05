About
============

Extends plone content with ability to render external content in viewlet.

Installing
============

This package requires Plone 3.x or later (tested on 3.3.x).

Installing without buildout
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install this package in either your system path packages or in the lib/python
directory of your Zope instance. You can do this using either easy_install or
via the setup.py script.

Installing with buildout
~~~~~~~~~~~~~~~~~~~~~~~~

If you are using `buildout`_ to manage your instance installing
collective.externalsnippet is even simpler. You can install
collective.externalsnippet by adding it to the eggs line for your instance::

    [instance]
    eggs = collective.externalsnippet

After updating the configuration you need to run the ''bin/buildout'', which
will take care of updating your system.

.. _buildout: http://pypi.python.org/pypi/zc.buildout

Usage
=====

Install "External Snippet" via Quick Installer, go to your content which you can publish external
content on and assign it marker interface "collective.externalsnippet.interfaces.IExternalSnippetMarker".
You can mark the content via ZMI on content's "Interfaces" tab or you can use "collective.interfaces_"
to do it in the Plone UI.

This adds to your content some extra fields which you can find in it's edit form on "Settings" tab where
you can specify URL address of external page you would like to fetch and render below your content's body.

You can also enter regular expression which will select particular content of fetched page (see default
value for an example).

It is also possible to fetch external pages guarded by basic authentication by entering required username
and password.

.. _collective.interfaces: http://plone.org/products/collective.interfaces

Copyright and Credits
=====================

collective.externalsnippet is licensed under the GPL. See LICENSE.txt for details.

Author: `Lukas Zdych (lzdych)`__ - development, maintenance, Czech translation

.. _lzdych: mailto:lukas.zdych@gmail.com

__ lzdych_

Sponsored by: `Auto Kelly, a.s.`__

.. _ak: http://autokelly.cz

__ ak_

