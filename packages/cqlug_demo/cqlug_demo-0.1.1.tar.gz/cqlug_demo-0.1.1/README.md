CQLug Demo - August 2012
========================

## Goal

Provide a demo of how to create a simple pypi package for all your python scripts.

- Use github to store the source code for all your python scripts
- Use pypi to store an installable package containing all your custom python scripts
 - Conveniently pip install your package to any of your machines

## Creating Sources

The easiest way:

- Make a github account
- Fork an existing package that is similar (e.g. stonier/cqlug_demo)

Alternatively create a new repo and add some files to your package.
Some notes on the structure and the files you'll need for pypi packaging.

<pre>
 - setup.py : list of python files, meta info required for your pypi package
 - MANIFEST.in : describes what regular files should be added (e.g. docs)
 - Makefile : convenience build targets so you don't have to remember them
 - make.bat : same thing for windows
 - src/pkg_name/__init.py__ : python module header file (declares api)
 - src/pkg_name/*.py : python module files (module implementation)
 - src/scripts/* : executable python scripts
</pre>

The python scripts are most easily managed if they are almost empty and just
call your module api.

## Building

Preparation, you need the python setuptools.

<pre>
> sudo apt-get install python-setuptools
</pre>

Two main use cases. While developing, it's easy to just install/uninstall directly.

<pre>
> make build
> sudo make install
# Test your python scripts
> sudo make uninstall
</pre>

## Adding to your Module

- create or add functions to your library in src/pkg_name/*.py
 - you can do this in existing files or by creating new .py files
- declare those functions in __init__.py
- create a script which calls your functionality in /scripts/mynewscript
- add the script filename to setup.py

## Creating the Package

- Create a pypi account.
- Register the package with pypi

<pre>
> make register
</pre>

You will see:

<pre>
running register
We need to know who you are, so please choose either:
    1. use your existing login,
    2. register as a new user,
    3. have the server generate a new password for you (and email it to you), or
    4. quit
Your selection [default 1]:
</pre>

Choose 1 or 2 and set up for your account locally. Finally, upload.

<pre>
make upload
</pre>

Go to http://pypi.python.org/ and login. You will see your package and the details there.

## Installing Pypi Packages

This can be done on almost any *nix machine. Windows is also possible, though I prefer creating msi installers for windows.

Install pip, the python package installer:

<pre>
> sudo apt-get install python-pip
</pre>

Then pip install your package:

<pre>
> sudo pip install -U cqlug_demo
# To uninstall
> sudo pip uninstall cqlug_demo
</pre>

