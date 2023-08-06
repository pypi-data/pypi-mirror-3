# -*- coding: utf-8 -*-
#
#  setup.py
#  globetrotter
#

"""
Packaging for globetrotter.
"""

import os
from setuptools import setup

readme = os.path.join(os.path.dirname(__file__), 'README.md')
readme_txt = open(readme).read() if os.path.exists(readme) else ''

setup(
    name='globetrotter',
    version='0.1.0',
    description='Approximate country and language name matching.',
    long_description=readme_txt,
    author='Lars Yencken',
    author_email='lars@yencken.org',
    url='http://bitbucket.org/larsyencken/globetrotter',
    py_modules=['globetrotter'],
    install_requires=[
            'pycountry==0.14.3',
            'wsgiref==0.1.2',
        ],
    license='ISC',
)
