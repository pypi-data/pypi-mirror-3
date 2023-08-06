# -*- coding: utf-8 -*-
html_use_modindex = False
html_use_index = False

source_suffix = '.rst'
master_doc = 'index'

project = u'Sphinx htmlslide sample'
copyright = u'2011, Sphinx-users.jp'

################################################################
# Extension and Theme setting
# You need to install `easy_install sphinxjp.themes.sphinxjp`

extensions = ['sphinxjp.themecore']
html_theme = 'htmlslide'

################################################################
# syntax highlighting style
pygments_style = 'monokai'


