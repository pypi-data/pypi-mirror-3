"""!

This file contains all of the exception objects used
to handle errors.
"""
from exceptions import Exception

#---------------------------------------------------------------------------

class CompileError(Exception):
    pass

#---------------------------------------------------------------------------

class ConnectError(Exception):
    pass

#---------------------------------------------------------------------------

class InputError(Exception):
    pass

#---------------------------------------------------------------------------

class OutputError(Exception):
    pass

#---------------------------------------------------------------------------

class ParameterSetError(Exception):
    pass

#---------------------------------------------------------------------------

class PluginDirectoryError(Exception):
    pass

#---------------------------------------------------------------------------

class PluginFileError(Exception):
    pass

#---------------------------------------------------------------------------

class PluginError(Exception):
    pass

#---------------------------------------------------------------------------

class RuntimeError(Exception):
    pass

#---------------------------------------------------------------------------

class ScheduleeError(Exception):
    pass

#---------------------------------------------------------------------------

class ScheduleeCreateError(Exception):
    pass

#---------------------------------------------------------------------------

class ScheduleError(Exception):
    pass

#---------------------------------------------------------------------------

class SolverError(Exception):
    pass

#---------------------------------------------------------------------------


class ServiceError(Exception):
    pass

#---------------------------------------------------------------------------
    
