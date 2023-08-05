#!/usr/bin/env python

from setuptools import setup

setup(
    name='rstyoutube',
    version='0.1',
    description='A directive to embed youtube videos in reStructuredText documents',
    long_description=open('README.txt').read(),
    author='J. Cliff Dyer',
    author_email='jcd@sdf.lonestar.org',
    url='http://bitbucket.org/cliff/rstyoutube',
    py_modules=['rstyoutube'],
    #package_data={'rstyoutube': ['examples/*']},
    scripts=['bin/rst2html+youtube.py'],
    license='LICENSE.txt',
    install_requires=[
        'docutils',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Topic :: Documentation',
    ],
)
