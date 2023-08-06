#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

release_notes = r"""
===============
Release Notes :
===============

Release 0.1:
============

First Version

Release 0.2:
============

Fixed a typo in this doc

"""

doc = r"""
This module enhances minidom and will allow you to have ordered
attributes instead of having them sorted automaticaly.

It is relevent in the fact that you may want to script the
loading/modification/saving of xml files and then print out a diff.
with the normal minidom since attributes are sorted automaticaly you can
have an unwanted diff for each unchaged line just because the order of
the attributes changed.

once you load this module, just use minidom normaly.

example::

    >>> from xml.dom import minidom
    >>> import enhancedminidom

then use minidom normaly except that:

+ Document and Element classes have a 'getElementsByAttributeName'
  method which can be verry handy.
+ 'toxml' and 'toprettyxml' will print attributes in the order they are
  created/loaded if 'minidom.SORTEDATTRIBUTES = False' (default)

example to get all nodes having a "foo" attribute::

    >>> document = minidom.parse('yourfile.xml')
    >>> nodes_with_foo = document.getElementsByAttributeName('foo')

example to get all nodes having a "foo" attribute if they are in a "fum" tag::

    >>> document = minidom.parse('yourfile.xml')
    >>> nodes_with_foo = document.getElementsByAttributeName('foo', 'fum')

"""

setup(name='enhancedminidom',
    version='0.2',
    author='Yves-Gwenael Bourhis',
    author_email='ygbourhis at gmail.com',
    description = "Enhance minidom in order to have ordered (instead of sorted) attributes, and a 'getElementsByAttributeName' method",
    license = 'GNU General Public License version 2.0',
    platforms = ['Windows','Linux','Mac OS',],
    long_description = str('\n'.join([doc, release_notes])),
    py_modules = ['enhancedminidom']
)
