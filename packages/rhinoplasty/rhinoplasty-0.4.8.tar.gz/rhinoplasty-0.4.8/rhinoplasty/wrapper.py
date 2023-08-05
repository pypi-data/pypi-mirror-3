"""Helper functions for wrapping one object inside a similar object.

These are often helpful when implementing decorators.
"""

from nose.tools import make_decorator
import inspect


def wrap_test_function(original):
    """Decorator to wrap a test function.
    
    This will copy any relevant metadata from the original function to the new
    definition.
    
    @param original: The original function that is being wrapped.
    """
    if not callable(original):
        raise ValueError("Original function is not actually a function.")
    
    # Just use the standard Nose function wrapper
    #TODO investigate whether any changes need to be made to the standard function
    return make_decorator(original)


def wrap_test_class(original):
    """Decorator to wrap a test suite.
    
    This will copy any relevant metadata from the original class to the new
    definition.
    
    @param original: The original class that is being wrapped.
    """
    if not inspect.isclass(original):
        raise ValueError("Original class is not actually a class.")
    
    def decorate(replacement):
        if not inspect.isclass(replacement):
            raise ValueError("Replacement class is not actually a class.")
        
        # Copy class name and module
        replacement.__name__ = original.__name__
        replacement.__module__ = original.__module__
        
        # Update the docstring, if possible
        # New-style objects do not permit this.
        try:
            replacement.__doc__ = original.__doc__
        except AttributeError:
            pass
        
        # Copy metadata across. We can't necessarily copy attributes directly,
        # and we need to filter them anyway.
        for name in dir(original):
            # Ignore special attributes
            if name[:2] == "__" and name [-2:] == "__":
                continue
            
            # Get the actual attribute
            value = getattr(original, name)
            
            # Do not copy methods (obviously).
            if callable(value):
                continue
            
            # Don't replace existing attributes
            if hasattr(replacement, name):
                continue
            
            setattr(replacement, name, value)
            
        return replacement
    
    return decorate


class ExampleClass(object):
    @classmethod
    def class_func(cls):
        pass
    
    def func(self):
        pass

callable(ExampleClass.func)
callable(getattr(ExampleClass, 'func'))
callable(ExampleClass.__dict__['func'])

callable(ExampleClass.class_func)
callable(getattr(ExampleClass, 'class_func'))
callable(ExampleClass.__dict__['class_func'])


def wrap_test_fixture(original):
    """Decorator to wrap a test case or test suite.
    
    This will copy any relevant metadata from the original test to the new
    definition.
    
    @param original: The original class or function that is being wrapped.
    """
    if inspect.isclass(original):
        return wrap_test_class(original)
    elif callable(original):
        return wrap_test_function(original)
    else:
        raise ValueError("Decorated object type is not recognised")
