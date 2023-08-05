# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os, sys

version = '0.1.0'
long_description = \
        open(os.path.join("src","README.txt")).read() + \
        open(os.path.join("src","AUTHORS.txt")).read() + \
        open(os.path.join("src","TODOS.txt")).read() + \
        open(os.path.join("src","HISTORY.txt")).read()

classifiers = [
    "Development Status :: 4 - Beta",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python",
    "Topic :: Software Development",
    "Topic :: Software Development :: Documentation",
    "Topic :: Text Processing :: Markup",
]

setup(
    name='sphinxjp.themes.solarized',
    version=version,
    description='A sphinx theme based on solarized color scheme. #sphinxjp',
    long_description=long_description,
    classifiers=classifiers,
    keywords=['sphinx', 'reStructuredText', 'solarized'],
    author='Takahiro MINAMI',
    author_email='vo dot gu dot ba dot miiton at gmail dot com',
    url='http://bitbucket.org/miiton/sphinxjp.themes.solarized',
    license='MIT',
    namespace_packages=['sphinxjp', 'sphinxjp.themes'],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    package_data = {'': ['buildout.cfg']},
    include_package_data=True,
    install_requires=[
        'setuptools',
        'docutils',
        'sphinx',
        'sphinxjp.themecore',
    ],
    entry_points="""
        [sphinx_themes]
        path = sphinxjp.themes.solarized:template_path

    """,
    zip_safe=False,
)

