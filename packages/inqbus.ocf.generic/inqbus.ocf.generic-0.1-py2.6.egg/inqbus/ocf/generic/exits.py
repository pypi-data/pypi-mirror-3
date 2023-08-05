from __future__ import print_function

import sys
import os
import syslog

class OcfError(SystemExit):
    def __init__(self, code, message):
        message = self.__class__.__name__ + "\n" + str(message)
        if not 'OCF_RESOURCE_INSTANCE' in os.environ:
            print(message, file=sys.stderr)
        syslog.syslog(syslog.LOG_ERR, "Agent exited with exitcode %s, %s" % (code, message))
        SystemExit.__init__(self, code)

class OCF_ERR_GENERIC(OcfError):
    def __init__(self, message):
        OcfError.__init__(self, 1, message)

class OCF_ERR_ARGS(OcfError):
    def __init__(self, message):
        OcfError.__init__(self, 2, message)

class OCF_ERR_UNIMPLEMENTED(OcfError):
    def __init__(self, message):
        OcfError.__init__(self, 3, message)

class OCF_ERR_PERM(OcfError):
    def __init__(self, message):
        OcfError.__init__(self, 4, message)

class OCF_ERR_INSTALLED(OcfError):
    def __init__(self, message):
        OcfError.__init__(self, 5, message)

class OCF_ERR_CONFIGURED(OcfError):
    def __init__(self, message):
        OcfError.__init__(self, 6, message)

class OCF_NOT_RUNNING(OcfError):
    def __init__(self, message=None):
        OcfError.__init__(self, 7, message)

class OCF_RUNNING_MASTER(OcfError):
    def __init__(self, message=None):
        OcfError.__init__(self, 8, message)

class OCF_FAILED_MASTER(OcfError):
    def __init__(self, message):
        OcfError.__init__(self, 9, message)
