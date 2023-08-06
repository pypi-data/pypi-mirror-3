===========
Tooth.paste
===========

Tooth.paste creates shiny new Python packages. Start your new packages with a prepared
Sphinx documentation section, a test folder for your unit tests and a Makefile containing
all the tools needed to keep your Python code clean. 

To get started:

    $ cd tooth.paste
    $ virtualenv --no-site-packages .
    $ bin/python setup.py develop

Create a basic namespace Python package:

    $ ./bin/templer tooth_basic_namespace

Inside of this new Python package you can directly run make:

- To get started with the new package:

    make build

- To build the html Sphinx documentation:

    make docs

- Have a look at the documentation:

    docs/build/html/index.html 

- To run the unit tests:

    make test

- To run the coverage:

    make coverage
  
- To run pylint:

    make pylint

- To run flake8:

    make flake8

- To run pep8:

    make pep8
