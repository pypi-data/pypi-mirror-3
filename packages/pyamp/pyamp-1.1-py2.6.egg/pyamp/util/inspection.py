from sys import modules
from inspect import getmembers, isclass, isfunction, ismodule


def getModules(moduleName):
    '''Get a dictionary mapping a module name to the actual module object for
    all of the modules in the given module name.

    .. note:: This function will raise an Exception in the event that the given
       module name is not importable.

    * moduleName -- The name of the module

    '''
    # If the module has not been imported yet, try to import it
    if moduleName not in modules:
        __import__(moduleName)

    # Return a list of all of the classes for this module
    return dict(getmembers(modules[moduleName], ismodule))


def getClasses(moduleName):
    '''Get a dictionary mapping a class name to the actual class object for all
    of the classes in the given module name.

    .. note:: This function will raise an Exception in the event that the given
       module name is not importable.

    * moduleName -- The name of the module

    '''
    # If the module has not been imported yet, try to import it
    if moduleName not in modules:
        __import__(moduleName)

    # Return a list of all of the classes for this module
    return dict(getmembers(modules[moduleName], isclass))


def getFunctions(moduleName):
    '''Get a dictionary mapping a function name to the actual function object
    for all of the functions in the given module name.

    .. note:: This function will raise an Exception in the event that the given
       module name is not importable.

    * moduleName -- The name of the module

    '''
    # If the module has not been imported yet, try to import it
    if moduleName not in modules:
        __import__(moduleName)

    # Return a list of all of the classes for this module
    return dict(getmembers(modules[moduleName], isfunction))
