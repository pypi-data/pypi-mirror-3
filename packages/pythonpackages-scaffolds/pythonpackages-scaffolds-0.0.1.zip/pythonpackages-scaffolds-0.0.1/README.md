pythonpackages-scaffolds
========================

PasteScript paster templates for pythonpackages.com

What is a scaffold?
-------------------

A scaffold is another name for a PasteScript paster template.

What is PasteScript?
--------------------

From http://pypi.python.org/pypi/PasteScript:: 

    "A pluggable command-line frontend, including commands to setup package file layouts".

Why?
----

This package was created for pythonpackages.com.

Scaffolds
---------

This package includes the following scaffolds:

- ``plone_theme``: Diazo theme for Plone 4

Installation
------------

Install with::

    $ {easy_install, pip} install pythonpackages-scaffolds

Usage
-----

Use with::

    $ paster create -t plone_theme plonetheme.name
