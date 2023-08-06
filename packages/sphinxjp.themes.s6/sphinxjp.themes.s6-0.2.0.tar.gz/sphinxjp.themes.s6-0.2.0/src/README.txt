S6 style presetation theme for Sphinx.

Output Sample
==============
:output: http://packages.python.org/sphinxjp.themes.s6/
:source: http://packages.python.org/sphinxjp.themes.s6/_sources/index.txt


Features
========
* provide ``s6`` directive for s6 presetation slide control.
* provide ``s6`` theme for render presetation.


Setup
=====
Make environment with easy_install::

    $ easy_install sphinxjp.themes.s6


Convert Usage
==============
setup conf.py with::

    extensions = ['sphinxjp.themecore']
    html_theme = 's6'

and run::

    $ make html


Writing s6 directive
=====================
slide paging effect::

    .. s6:: effect slide

ul elements move from (0,0) to (100,0) position in 5.0 secs::

    .. s6:: actions

        ['ul', 'move', '5.0', [0,0],[100,0]]

set html styles to target slide::

    .. s6:: styles

        h2: {fontSize:'150%', textAlign:'center', margin:'30% auto'}

This is a little complex example::

    .. s6:: styles

        'ul/li': {display:'none'}

    .. s6:: actions

        ['ul/li[0]', 'fade in', '0.3'],
        ['ul/li[1]', 'fade in', '0.3'],
        ['ul/li[2]', 'fade in', '0.3'],


Requirements
============
* Python 2.4 or later (not support 3.x)
* sphinx 1.0.x or later.

Presentation Environments
==========================
* Internet Explorer 8.0
* Firefox 3.6.x
* Chrome / Safari


License
=======
Licensed under the `MIT license <http://www.opensource.org/licenses/mit-license.php>`_ .
See the LICENSE file for specific terms.

