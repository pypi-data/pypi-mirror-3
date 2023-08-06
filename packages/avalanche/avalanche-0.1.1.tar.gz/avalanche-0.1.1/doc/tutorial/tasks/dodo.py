import glob

from doit.tools import InteractiveAction


DOIT_CONFIG = {'default_tasks': ['checker', 'ut']}

py_modules = glob.glob("*.py")
py_tests = glob.glob("tests/test_*.py")


SKIP_CHECKER = set(['webapp2.py'])

def task_checker():
    """run pyflakes on all project modules"""
    for module in py_modules:
        if module in SKIP_CHECKER:
            continue
        yield {'actions': ["pyflakes %s"% module],
               'name':module,
               'file_dep':(module,),
               'title': (lambda task: task.name)}

def task_ut():
    """run unit-tests"""
    for test in py_tests:
        yield {'name': test,
               'actions': ["py.test %s" % test],
               'file_dep': py_modules + [test],
               'verbosity': 0}


def task_coverage():
    """show coverage for all modules including tests"""
    return {'actions':[
            "coverage run `which py.test` tests ",
            "coverage report --omit=webapp2.py,avalanche.py,dodo.py "
                "--show-missing %s" % " ".join(py_modules + py_tests),
            ],
            'verbosity': 2}


def task_serve():
    """run developemnt server"""
    cmd = "dev_appserver.py --datastore_path dev.db ."
    return {'actions': [InteractiveAction(cmd)],
            }
