import pep8
import py
import pytest

__version__ = '0.9.1'


def pytest_addoption(parser):
    group = parser.getgroup("general")
    group.addoption('--pep8', action='store_true',
        help="perform some pep8 sanity checks on .py files")
    parser.addini("pep8ignore", type="args",
        help="warning/errors to ignore, example value: W293 W292")


def pytest_collect_file(path, parent):
    if parent.config.option.pep8 and path.ext == '.py':
        return Pep8Item(path, parent)


def pytest_configure(config):
    if config.option.pep8:
        config._pep8ignore = config.getini("pep8ignore")


def pytest_report_header(config):
    pep8ignore = getattr(config, '_pep8ignore', None)
    if pep8ignore is not None:
        if pep8ignore:
            pep8ignore = " ".join(pep8ignore)
        else:
            pep8ignore = "(performing all available checks)"
        return "pep8 ignore opts: " + pep8ignore


class Pep8Error(Exception):
    """ indicates an error during pep8 checks. """


class Pep8Item(pytest.Item, pytest.File):
    def __init__(self, path, parent):
        super(Pep8Item, self).__init__(path, parent)
        self.keywords['pep8'] = True

    def runtest(self):
        call = py.io.StdCapture.call
        pep8ignore = self.config._pep8ignore
        found_errors, out, err = call(check_file, self.fspath, pep8ignore)
        if found_errors:
            raise Pep8Error(out, err)

    def repr_failure(self, excinfo):
        if excinfo.errisinstance(Pep8Error):
            return excinfo.value.args[0]
        return super(Pep8Item, self).repr_failure(excinfo)

    def reportinfo(self):
        return (self.fspath, -1, "PEP8-check")


def check_file(path, pep8ignore):
    options, args = pep8.process_options([
        '--ignore=%s' % (",".join(pep8ignore)),
        '--show-source',
        str(path),
    ])
    del options.filename
    checker = PyTestChecker(args[0], **options.__dict__)
    return checker.check_all()


class PyTestChecker(pep8.Checker):
    ignored_errors = 0
    #def report_error(self, line_number, offset, text, check):
    #    # XXX hack
    #    if pep8.ignore_code(text[:4]):
    #        self.ignored_errors += 1
    #    pep8.Checker.report_error(self, line_number, offset, text, check)
