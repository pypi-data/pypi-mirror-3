Createcoverage
==============

This package installs one command: ``createcoverage`` that runs your tests
with coverage.py and opens the coverage reports in your browser.  All with
just one single handy command.

Assumption: you're using buildout.  Or rather, the assumption is that you have
a ``bin/test`` command that runs all your tests.

No options are passed to coverage.py, so any extra options you want to give to
coverage must be put in a ``.coveragerc`` in your buildout's root.  This is a
good idea in any case :-)  An example .coveragerc that omits code you normally
don't want to include in a coverage report::

    [report]
    omit =
        /home/*/.buildout/eggs/*
        /usr/*
        parts/*
        eggs/*
        */test*

Installing ``createcoverage`` in a zc.recipe.egg section is enough.
Createcoverage itself depends on `coverage.py
<http://nedbatchelder.com/code/coverage/>`_ and makes sure ``bin/coverage`` is
created::

  [console_scripts]
  recipe = zc.recipe.egg
  eggs = createcoverage


Code, bugs, ideas
-----------------

The code is hosted at bitbucket: https://bitbucket.org/reinout/createcoverage
.

You can also report `issues and bugs and ideas
<https://bitbucket.org/reinout/createcoverage/issues>`_ there.


Development installation
------------------------

The first time, you'll have to run the "bootstrap" script to set up setuptools
and buildout::

    $> python bootstrap.py

And then run buildout to set everything up::

    $> bin/buildout

(On windows it is called ``bin\buildout.exe``).

You'll have to re-run buildout when you or someone else made a change in
``setup.py`` or ``buildout.cfg``.

The current package is installed as a "development package", so
changes in .py files are automatically available (just like with ``python
setup.py develop``).

Tests can always be run with ``bin/test`` or ``bin\test.exe``.
