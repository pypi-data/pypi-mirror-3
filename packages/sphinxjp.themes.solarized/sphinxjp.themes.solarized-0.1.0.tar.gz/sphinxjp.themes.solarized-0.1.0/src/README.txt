A sphinx theme based on solarized color scheme.

Output Sample
==============================================================================
http://docs.btnb.jp/solarized_theme/

Features
==============================================================================
* provide ``solarized`` directive for render HTML document.


Setup
==============================================================================
Make environment with easy_install::

    $ easy_install sphinxjp.themes.solarized


Convert Usage
==============================================================================
setup conf.py with::

    extensions = ['sphinxjp.themecore', 'sphinxjp.themes.solarized']
    html_theme = 'solarized'

and run::

    $ make html

Requirements
==============================================================================
* Python 2.4 or later (not support 3.x)
* sphinx 1.0.x or later.

License
==============================================================================
Licensed under the `MIT license <http://www.opensource.org/licenses/mit-license.php>`_ .
See the LICENSE file for specific terms.

