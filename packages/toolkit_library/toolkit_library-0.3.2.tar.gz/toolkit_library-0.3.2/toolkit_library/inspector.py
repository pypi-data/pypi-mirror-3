"""
    toolkit_library.inspector
    ~~~~~~~~~~~~~~~~~~~~~~~~
    Inspect functions in a module and invoke them
    Notice:
        method name promption used raw_input
        method parameter promption used input
        Python3 raw_input becomes input and input disappears. If you want input, you can use eval(raw_input)
"""
import inspect


class ModuleInspector(object):
    """Inspect the functions in a module for invoking
    Sample usage:
        inspector = ModuleInspector(module)
        inspector.invoke() # inspect the available functions and invoke one
        inspector.invoke('foo') # invoke function foo in module
        inspector.invoke('bar', 'hello') # invoke function bar in module and provide one argument 'hello'
    If no function name was specified, you will be prompted to specify one;
    If not enough arguments were specified, you will be prompted to specify them.
    """
    def __init__(self, module):
        if not inspect.ismodule(module):
            raise TypeError('{0} is not a valid python module'.format(module))
        self.module = module

    def invoke(self, function_name = None, *args):
        """Invoke a function of the module"""
        predicate = inspect.isfunction
        if not function_name:
            print 'The following functions are available in {0}:'.format(self.module.__file__)
            print '====================================================='
            for name, value in inspect.getmembers(self.module, predicate):
                print '[{0}]: {1}'.format(name, value.__doc__)
            print '====================================================='
            return self.invoke(raw_input('Please enter the function name which you want to invoke: '), *args) # recursive call with user input as parameter

        functions = [value for (name, value) in inspect.getmembers(self.module, predicate) if name == function_name]
        if not functions:
            raise Exception('{0} has no function "{1}" defined'.format(self.module.__file__, function_name))

        function = functions[0] # the function to be invoked
        required_args, _, _, defaults = inspect.getargspec(function) # required args of the function
        if not required_args: # the function does not need args
            return function()

        if len(args) >= len(required_args): # enough args are provided
            return function(*args[:len(required_args)])

        args = list(args)
        missing_args = required_args[len(args):]
        defaults = defaults if defaults else []
        if len(defaults) >= len(missing_args): # enough default values
            args.extend(defaults[-len(missing_args):])
            return function(*args)

        for i in range(len(missing_args) - len(defaults)): # prompt user for args
            args.append(input('Please enter the value of parameter "{0}": '.format(missing_args[i])))
        args.extend(defaults) # Plus the default args
        return function(*args)

    def get_all_classes(self):
       """Return all of the class names in the modoule as a list"""
       members = inspect.getmembers(self.module, lambda model: inspect.isclass(model) and model.__module__ == self.module.__name__) 
       return [name for name, _ in members]

    def import_all_classes_statement(self):
       """The statement for Importing all of the classes in the module"""
       return 'from {0} import {1}'.format(self.module.__name__, ', '.join(self.get_all_classes()))
