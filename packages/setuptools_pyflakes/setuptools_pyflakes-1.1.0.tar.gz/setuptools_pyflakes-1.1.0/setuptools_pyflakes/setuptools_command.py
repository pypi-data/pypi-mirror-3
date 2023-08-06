import os

import pkg_resources, setuptools

import pyflakes
from pyflakes import checker

import sys

def check(codeString, filename):
    try:
        if pkg_resources.parse_version(pyflakes.__version__) >= (0,5,0):
            import _ast
            tree = compile(codeString, filename, "exec", _ast.PyCF_ONLY_AST)
        else:
            import compiler
            # for pyflakes < 0.5
            tree = compiler.parse(codeString)
    except (SyntaxError, IndentationError):
        value = sys.exc_info()[1]
        try:
            (lineno, offset, line) = value[1][1:]
        except IndexError:
            print >> sys.stderr, 'could not compile %r' % (filename,)
            return 1
        if line.endswith("\n"):
            line = line[:-1]
        print >> sys.stderr, '%s:%d: could not compile' % (filename, lineno)
        print >> sys.stderr, line
        print >> sys.stderr, " " * (offset-2), "^"
        return 1
    else:
        w = checker.Checker(tree, filename)
        w.messages.sort(lambda a, b: cmp(a.lineno, b.lineno))
        for warning in w.messages:
            print warning
        return len(w.messages)

def checkPath(filename):
    if os.path.exists(filename):
        return check(file(filename, 'U').read() + '\n', filename)

class PyflakesCommand(setuptools.Command):
    description = "run pyflakes on all your modules"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        warnings = False
        base = self.get_finalized_command('build_py')
        for (package, module, file) in base.find_all_modules():
            if checkPath(file):
                warnings=True
        if warnings:
            sys.exit(1) # FAIL
