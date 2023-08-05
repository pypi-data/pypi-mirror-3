
class OcfError(SystemExit):
    def __init__(self, code, message):
        SystemExit.__init__(self, code)
        self.message = message

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