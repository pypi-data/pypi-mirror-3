====================
cmsplugin-nivoslider
====================

Simple image slider plugin.
Shows the widely used jquery Nivo slider plugin from http://nivo.dev7studios.com/

Features:

- Four default nivo slider theme choices
- User selection of nivo parameters: nivo theme, animation effect, speed, pause...
- Auto-discovering of custom nivo themes on static dirs
- Provides a very simple model for storing images and albums.

Requires:
- easy-thumbnails http://pypi.python.org/pypi/easy-thumbnails/


Installation
============

#. `pip install cmsplugin_nivoslider`
#. Add `'cmsplugin_nivoslider'` to `INSTALLED_APPS`
#. Run `syncdb` or `./manage.py migrate cmsplugin_nivoslider` if using south

You need to have correctly configured staticfiles for autodiscovering and using themes

Using a custom or downloaded theme
==================================

When reloading your django app, the plugin will search for themes on the following
static dir: `nivo/themes/`

So all you need to do is puting your theme plugin on  `static/nivo/themes/pluginname`
dir of some app of your django project. 

So after collectstatic, theme wil be available under the directory:
`STATIC_ROOT/nivo/themes/pluginname`
And will be found by cmsplugin_nivoslider.

:Authors:

- Bernardo Cabezas serra - bcabezas@apsl.net - http://www.apsl.net/
- Bertrand Bordage

:Initial version date: 2012/03/14
