import unittest
import doctest

# import testable modules
mods = []
for name in ['reader', 'writer', 'model', 'munger', 'filter', 'formatter', 'options']:
    parent = __import__('todopy.' + name)
    mods.append(getattr(parent, name))


def load_tests(loader, tests, ignore):
    #tests.addTests(doctest.DocFileSuite('../../todo.py'))
    for mod in mods:
        try:
            tests.addTests(doctest.DocTestSuite(mod))
        except ValueError:
            pass
    return tests

