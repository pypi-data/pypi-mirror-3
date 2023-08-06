py.test plugin for checking PEP8 source code compliance using the `pep8 module <http://pypi.python.org/pypi/pep8>`_.

Usage
---------

install via::

    easy_install pytest-pep8 # or
    pip install pytest-pep8

and then type::

    py.test --pep8
    
to activate source code checking. Every file ending in ``.py`` will be
discovered and checked, starting from the command line arguments.
For example, if you have a file like this::

    # content of myfile.py
 
    somefunc( 123,456)

you can run it with::

    $ py.test --pep8
    =========================== test session starts ============================
    platform linux2 -- Python 2.6.5 -- pytest-2.0.1.dev1
    pep8 ignore opts: (performing all available checks)
    collecting ... collected 1 items
    
    myfile.py F
    
    ================================= FAILURES =================================
    ________________________________ PEP8-check ________________________________
    /tmp/doc-exec-20/myfile.py:2:10: E201 whitespace after '('
    somefunc( 123,456)
             ^
    /tmp/doc-exec-20/myfile.py:2:14: E231 missing whitespace after ','
    somefunc( 123,456)
                 ^
    
    ========================= 1 failed in 0.01 seconds =========================

In the testing header you will always see the list of pep8 checks that are ignored
(non by default).  For the meaning of these error and warning codes, see the error
output when running against your files or checkout `pep8.py
<https://github.com/jcrocholl/pep8/blob/master/pep8.py>`_.

Configuring PEP8 options per-project
---------------------------------------------

You may configure PEP8-checking options for your project
by adding an ``pep8ignore`` entry to your ``pytest.ini``
or ``setup.cfg`` file like this::

    # content of pytest.ini
    [pytest]
    pep8ignore = E201 E231

This would prevent complaints about some whitespace issues (see above).
Rerunning it with the above example will now look better::

    $ py.test -q --pep8
    collecting ... collected 1 items
    .
    1 passed in 0.01 seconds

Running PEP8 checks and no other tests
---------------------------------------------

You can also restrict your test run to only perform "pep8" tests
and not any other tests by typing::

    py.test --pep8 -k pep8

This will only run tests that are marked with the "pep8" keyword
which is added for the pep8 test items added by this plugin.

Notes
-------------

The repository of this plugin is at http://bitbucket.org/hpk42/pytest-pep8

For more info on py.test see http://pytest.org

The code is partially based on Ronny Pfannschmidt's pytest-codecheckers plugin.

