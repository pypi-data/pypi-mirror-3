"""
PyPoly Jinja2 Plugin
"""
import os
from setuptools import findall
from setuptools import setup

__author__ = 'PyPoly Team'

files =[
        (
            os.path.dirname(f),
            [f]
        ) for f in findall("pp_jinja2/templates")
]

setup(
    name='pypoly-plugin-jinja',
    version='0.1',
    description="Use Jinja2 in PyPoly applications",
    author=__author__,
    packages=['pp_jinja2'],
    data_files=files,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content"
    ],
    install_requires=[
        "pypoly >= 0.4",
        "jinja2"
    ],
    zip_safe = False,
    entry_points='''
    [pypoly.plugin]
    Jinja2 = pp_jinja2:Main
    '''

)
