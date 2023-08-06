import os
from Products.AROfficeTransforms.config import TIMEOUT


def command_exists(command):
    for path in os.environ["PATH"].split(os.pathsep):
        if os.path.exists(os.path.join(path, command)):
            return True
    else:
        return False


def timelimit():
    if command_exists('timelimit'):
        return "timelimit -t%d -T%d" %\
                (TIMEOUT['WARNTIME'], TIMEOUT['KILLTIME'])
    else:
        return ""
