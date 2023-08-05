# -*- coding: utf-8 -*-
import sys, os

extensions = [
                'sphinxjp.themecore',
                'sphinxjp.themes.solarized'
            ]
templates_path = ['_templates']
source_suffix = '.rst'

master_doc = 'index'

project = u'Solarized Sphinx Theme'
copyright = u'2011, Takahiro MINAMI'

version = '0.1'
release = '0.1'
language = 'ja'

exclude_patterns = ['_build']
pygments_style = 'solarized'

html_theme = 'solarized'
html_static_path = ['_static']
html_last_updated_fmt = '%Y/%m/%d %H:%M:%S'
htmlhelp_basename = 'SolarizedSphinxThemedoc'
