from setuptools import setup

setup(
    name='sphinx-naps-theme',
    version='1',
    description=('Sphinx theme used by Antoine Millet for its projects'),
    author='Antoine Millet',
    author_email='antoine@inaps.org',
    packages=['sphinx_naps_theme', 'sphinx_naps_theme.ext'],
    package_data = {'sphinx_naps_theme': ['themes/*/*.*', 'themes/*/static/*.*']},
    include_package_data=True
)
