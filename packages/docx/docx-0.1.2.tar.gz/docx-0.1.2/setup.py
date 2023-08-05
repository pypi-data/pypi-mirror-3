#!/usr/bin/env python
from setuptools import setup

setup(
    name='docx',
    version='0.1.2',
    requires=(
        'lxml', 
        'python_dateutil',
    ),
    description='The docx module creates, reads and writes Microsoft Office Word 2007 docx files',
    author='Mike MacCana',
    author_email='python.docx@librelist.com',
    url='http://github.com/mikemaccana/python-docx',
    packages=['docx'],
    package_data={
        'docx': ['docx/template/*']
    },
)
