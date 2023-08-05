napsTheme Sphinx Style
======================

This repository contains sphinx styles Antoine Millet uses in most of
his projects. It is a derivative of Kenneth Reitz's theme which is itself a
derivative of Mitsuhiko's themes for Flask and Flask related
projects.  To use this style in your Sphinx documentation, follow
this guide:

1. put this folder as _themes into your docs folder.  Alternatively
   you can also use git submodules to check out the contents there.

2. add this to your conf.py: ::

    sys.path.append(os.path.abspath('_themes'))
    html_theme_path = ['_themes']
    html_theme = 'naps'
