import re
import py
import pytest
import pep8

__version__ = '1.0.1'

HISTKEY = "pep8/mtimes"


def pytest_addoption(parser):
    group = parser.getgroup("general")
    group.addoption('--pep8', action='store_true',
        help="perform some pep8 sanity checks on .py files")
    parser.addini("pep8ignore", type="linelist",
        help="each line specifies a glob pattern and whitespace "
             "separated PEP8 errors or warnings which will be ignored, "
             "example: *.py W293")


def pytest_sessionstart(session):
    config = session.config
    if config.option.pep8:
        config._pep8ignore = Ignorer(config.getini("pep8ignore"))
        config._pep8mtimes = config.cache.get(HISTKEY, {})


def pytest_collect_file(path, parent):
    config = parent.config
    if config.option.pep8 and path.ext == '.py':
        pep8ignore = config._pep8ignore(path)
        if pep8ignore is not None:
            return Pep8Item(path, parent, pep8ignore)


def pytest_sessionfinish(session):
    config = session.config
    if hasattr(config, "_pep8mtimes"):
        config.cache.set(HISTKEY, config._pep8mtimes)


class Pep8Error(Exception):
    """ indicates an error during pep8 checks. """


class Pep8Item(pytest.Item, pytest.File):

    def __init__(self, path, parent, pep8ignore):
        super(Pep8Item, self).__init__(path, parent)
        self.keywords['pep8'] = True
        self.pep8ignore = pep8ignore

    def setup(self):
        pep8mtimes = self.config._pep8mtimes
        self._pep8mtime = self.fspath.mtime()
        old = pep8mtimes.get(str(self.fspath), (0, []))
        if old == (self._pep8mtime, self.pep8ignore):
            pytest.skip("file(s) previously passed PEP8 checks")

    def runtest(self):
        call = py.io.StdCapture.call
        found_errors, out, err = call(check_file, self.fspath, self.pep8ignore)
        if found_errors:
            raise Pep8Error(out, err)
        # update mtime only if test passed
        # otherwise failures would not be re-run next time
        self.config._pep8mtimes[str(self.fspath)] = (self._pep8mtime,
                                                     self.pep8ignore)

    def repr_failure(self, excinfo):
        if excinfo.errisinstance(Pep8Error):
            return excinfo.value.args[0]
        return super(Pep8Item, self).repr_failure(excinfo)

    def reportinfo(self):
        if self.pep8ignore:
            ignores = "(ignoring %s)" % " ".join(self.pep8ignore)
        else:
            ignores = ""
        return (self.fspath, -1, "PEP8-check%s" % ignores)


class Ignorer:
    def __init__(self, ignorelines, coderex=re.compile("[EW]\d\d\d")):
        self.ignores = ignores = []
        for line in ignorelines:
            try:
                glob, ign = line.split(None, 1)
            except ValueError:
                glob, ign = None, line
            if glob and coderex.match(glob):
                glob, ign = None, line
            if ign == "ALL":
                ign = None
            else:
                ign = ign.split()
            ignores.append((glob, ign))

    def __call__(self, path):
        l = []
        for (glob, ignlist) in self.ignores:
            if not glob or path.fnmatch(glob):
                if ignlist is None:
                    return None
                l.extend(ignlist)
        return l


def check_file(path, pep8ignore):
    checker = pep8.Checker(str(path), ignore=pep8ignore, show_source=1)
    return checker.check_all()
