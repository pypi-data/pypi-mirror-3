import types
import logging
from puke.Error import *
from puke.Console import *

__tasks__ = {}


def addTask(task):
    console.debug("Registering task: %s" % task.name)
    __tasks__[task.name] = task


def hasDefault():
    if 'default' not in __tasks__:
        return False
    
    return True
    
def executeTask(name):
    if name in __tasks__:
        console.header("-------------------------------------\n * Executing task: %s (%s) \n -------------------------------------" % (name, __tasks__[name].desc), 1)
        __tasks__[name]()
    else:
        raise PukeError("No such task: %s" % name)
        
def printTasks():
    for name in __tasks__:
        obj = __tasks__[name]
        if obj.desc:
            logging.info("%s: %s" % (name, obj.desc))
        else:
            logging.info("%s" % name)



class Task:
    __doc__ = ""
    
    def __init__(self, func, desc=""):
        name = func.__name__
        self.__func = func
        
        self.name = name
        self.desc = desc
        self.fullname = "%s.%s" % (func.__module__, name)
        
        try:
            self.__doc__ = func.__doc__
        except AttributeError:
            pass
            
        addTask(self)
        

    def __call__(self, *args, **kw):
        retval = self.__func()
        return retval


    def __repr__(self):
        return "Task: " + self.__name__



def task(func):
    """ Specifies that this function is a task. """
    
    if isinstance(func, Task):
        return func

    elif isinstance(func, types.FunctionType):
        return Task(func)
    
    else:
        # Used for descriptions
        def wrapper(finalfunc):
            return Task(finalfunc, func)
            
        return wrapper

    