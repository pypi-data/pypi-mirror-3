import glob

import pytest


DOIT_CONFIG = {'default_tasks': ['checker', 'ut',]}

ROOT_MODULES = glob.glob("*.py")
CODE_FILES = glob.glob("avalanche/*.py")
TEST_FILES = glob.glob("tests/test_*.py")
PY_MODULES = (ROOT_MODULES + CODE_FILES + TEST_FILES)
DOC_FILES = glob.glob("doc/*.rst")

SKIP_CHECKER = set(['setup.py'])


def task_checker():
    """run pyflakes on all project modules"""
    for module in PY_MODULES:
        if module in SKIP_CHECKER:
            continue
        yield {'actions': ["pyflakes %s" % module],
               'name':module,
               'file_dep':(module,),
               }

def run_test(test):
    return not bool(pytest.main(test))
def task_ut():
    """run unit-tests"""
    for test in TEST_FILES:
        yield {'name': test,
               'actions': [(run_test, (test,))],
               'file_dep': CODE_FILES,
               'verbosity': 0}

def task_coverage():
    """show coverage for all modules including tests"""
    return {'actions':
                ["coverage run --branch `which py.test` tests",
                 ("coverage report --show-missing %s" %
                  " ".join(CODE_FILES + TEST_FILES))
                 ],
            'verbosity': 2}


def task_coverage_code():
    """show coverage for all modules (exclude tests)"""
    return {'actions':
                ["coverage run --branch `which py.test` ",
                 "coverage report --show-missing %s" % " ".join(CODE_FILES)],
            'verbosity': 2}


def task_coverage_module():
    """show coverage for individual modules"""
    to_strip = len('tests/test_')
    for test in TEST_FILES:
        source = "avalanche/" + test[to_strip:]
        yield {'name': test,
               'actions':
                   ["coverage run --branch `which py.test` -v %s" % test,
                    "coverage report --show-missing %s %s" % (source, test)],
               'verbosity': 2}




####################################################################

############################ website


DOC_ROOT = 'doc/'
DOC_BUILD_PATH = DOC_ROOT + '_build/html/'

def task_sphinx():
    """generate website docs"""
    action = "sphinx-build -b html -d %s_build/doctrees %s %s"
    return {
        'actions': [action % (DOC_ROOT, DOC_ROOT, DOC_BUILD_PATH)],
        'file_dep': DOC_FILES + CODE_FILES,
        }

def task_manifest():
    """create manifest file for distutils """

    def check_version():
        # using a MANIFEST file directly is broken on python2.7
        # http://bugs.python.org/issue11104
        import sys
        assert sys.version_info < (2,7)

    cmd = "hg manifest > MANIFEST"
    return {'actions': [check_version, cmd]}


def task_pypi():
    """upload package to pypi"""
    return {
        'actions': ["python setup.py sdist upload"],
        'task_dep': ['manifest'],
        }


def task_website():
    """deploy website (sphinx docs)"""
    action = "python setup.py upload_docs --upload-dir %s"
    return {'actions': [action % DOC_BUILD_PATH],
            'task_dep': ['sphinx'],
            'verbosity': 2,
            }
