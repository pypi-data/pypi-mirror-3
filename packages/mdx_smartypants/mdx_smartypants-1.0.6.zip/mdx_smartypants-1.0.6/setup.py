#! /usr/bin/env python

from setuptools import setup

readme = open('README.txt', 'r')
README_TEXT = readme.read()
readme.close()

setup(
    name='mdx_smartypants',
    version='1.0.6',
    author='Jonathan Eunice',
    author_email='jonathan.eunice@gmail.com',
    description='Python-Markdown extension using smartypants to emit typographically nicer ("curly") quotes, proper ("em" and "en") dashes, etc.',
    long_description=README_TEXT,
    url='http://bitbucket.org/jeunice/mdx_smartypants',
    py_modules=['mdx_smartypants'],
    install_requires=['Markdown>=2.0','smartypants>=1.6','namedentities>=1.0.5'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Programming Language :: Python',
        'Topic :: Text Processing :: Filters',
        'Topic :: Text Processing :: Markup :: HTML'
    ]
)
