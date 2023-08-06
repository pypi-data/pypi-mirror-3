# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

# Utility function to read the README file.  
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except IOError:
        return ''

setup(
    name="redsolutioncms.django-tinymce",
    version=__import__('tinymce').__version__,
    description=read('DESCRIPTION'),
    license="MIT License",
    keywords="django widget tinymce",

    author="Joost Cassee",
    author_email="joost@cassee.net",

    url="http://code.google.com/p/django-tinymce/",

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: Freely Distributable',
        'Framework :: Django',
        'Environment :: Web Environment',
        'Natural Language :: Russian',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
    ],
    packages=find_packages(exclude=['testtinymce']),
    include_package_data=True,
    zip_safe=False,
    long_description=read('README'),
    download_url="http://code.google.com/p/django-tinymce/downloads/list",
    entry_points={
        'redsolutioncms': ['tinymce = tinymce.redsolution_setup', ],
    }
)
