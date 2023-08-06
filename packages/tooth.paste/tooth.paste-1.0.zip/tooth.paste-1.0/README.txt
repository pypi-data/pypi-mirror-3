.. contents::

Introduction
============

Install a virtualenv and setup the package to create the bin/templer script
and the Python project template:

    $ python/virtualenv --no-site-packages .
    $ cd tooth.paste
    $ bin/python setup.py develop

Create a custom basic Python project:

    $ ./bin/templer tooth_basic_namespace

The "tooth_basic_namespace" template should be available through templer:

    $ ./bin/templer --list
    tooth_basic_namespace: A custom basic Python project
    This creates a Tooth Python project.

