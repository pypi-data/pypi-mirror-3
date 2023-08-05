.. contents:: **Table of contents**

How it works
============

.. figure:: http://keul.it/images/plone/collective.flowplayer_toolbar-0.1.0.png
   :scale: 50
   :align: right
   :alt: Multiple player
   
   Multiple players inside a page.

This product use basic feature given to you from `Flowplayer`__.

__ http://flowplayer.org/

You must know that installing `collective.flowplayer`__ in your Plone site give you all the
Flowplayer power.
Unluckily the native Flowplayer's controlsbar is *not always accessible*: recent releases sometimes
are quite usable with keyboard, but not on every browser and not all features.
There's a `Flowplayer plugin`__ gives you the power to create and handle the player with an alternative
JavaScript controlsbar.

__ http://pypi.python.org/pypi/collective.flowplayer
__ http://flowplayer.org/plugins/javascript/controlbar.html

This product does exactly this task. The default Flash controlsbar of the player will be
disabled and a new, JavaScript based, ones will be shown providing some `WAI ARIA`__ attributes.

__ http://www.w3.org/WAI/intro/aria.php

If needed you can also enable again the native Flash controlsbar (as far as only there you can access
feature like the fullscreen view of your videos, due to security reasons).
To do this, put to ``True`` the ``toolbar_flash_controlsbar`` property in the *flowplayer_properties*
property sheet.

The controlsbar plugin provided is not the original one you can find on Flowplayer site, but is fixed
to be more accessible and fully *usable using keyboard*.

You can move around using the *TAB* key (and *SHIFT+TAB* for moving backward) and trigger button
with *ENTER*.

When the focus is on the *slider* that indicate the video progress, you can:

* move forward/back for 5 seconds with right/left keys
* move forward/back for 1 minute with *PAGE DOWN*/*PAGE UP* keys
* move at the beginning of the video with *HOME* key
* move at the end of the video with *END* key

If you don't care about accessibility of your videos, you don't need this package
(but obviously you are a bad guy).

Accessible slider help text
---------------------------

When you navigate with keyboard to the slider, giving it the focus, an help tooltip will be displayed
with instruction on how to use the slider with keyboard.

.. figure:: http://keul.it/images/plone/collective.flowplayer_toolbar-0.2.0.png
   :scale: 50
   :alt: Help on Plone 4
   
   How help text looks like (Plone 4).

The help text is provided in english (default), italian and danish. To support additional languages
you can modify the product source or (better) provide an additional Javascript registered *after* the
flowplayer.accessible.controls.js::

    jQuery.flowplayer_toolbar.slider_guide.xx = {
             intro:             'How to control the slider',
             left_arrow_label:  'Left arrow',
             left_arrow_help:   'backward 5 seconds',
             right_arrow_label: 'Right arrow',
             right_arrow_help:  'forward 5 seconds',
             page_up_label:     'Page up',
             page_up_help:      'backward 1 minute',
             page_down_label:   'Page down',
             page_down_help:    'forward 1 minute',
             home_label:        'Home key',
             home_help:         'go to beginning of clip',
             end_label:         'End key',
             end_help:          'go to end of clip'
    };

Change *xx* above with the 2-letters code of your language and customize other strings.
Language loaded is taken from the language of the site (for any problem, fallback on english).

If you like, send me your translation and see them becoming part of next release.

Dependencies
============

* `collective.flowplayer`__ (tested on version 3.0rc4)

__ http://pypi.python.org/pypi/collective.flowplayer

Works on those Plone versions:

* Plone 3.3
* Plone 4.1

Credits
=======

* Jacopo Deyla, from `Regione Emilia Romagna`__, for fixing the accessibility of the controlsbar plugin
  and giving help about WAI-ARIA technology and tests with the toolbar.
* T.C. Mogensen (tmog) for providing danish translation and doing tests with older Plone releases.

__ http://www.regione.emilia-romagna.it/

