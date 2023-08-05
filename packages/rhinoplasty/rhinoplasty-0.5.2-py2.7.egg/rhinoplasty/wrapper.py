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
    #TODO investigate whether any changes need to be made to the standard Nose function
    return make_decorator(original)


def wrap_test_class(original):
    """Decorator to wrap a test class.
    
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


def wrap_test_fixture(original):
    """Decorator to wrap a test function or test class.
    
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


def wrap_fixture_with_exception(ex):
    """Decorator that will raise an exception instead of running the tests in
    a test class or test function
    
    @param ex: Exception instance to raise.
    """
    def decorate(fixture):
        if inspect.isclass(fixture):
            # Create a replacement class that raises an appropriate exception
            @wrap_test_class(fixture)
            class ClassWrapper(object):
                def test_suite_raises_exception(self):
                    raise ex
                test_suite_raises_exception.__doc__ = fixture.__doc__
            
            return ClassWrapper
        
        elif callable(fixture):
            # Create a replacement function that raises an appropriate exception
            @wrap_test_function(fixture)
            def test_function_wrapper(*args):
                """Replaces a test and unconditionally raises an exception."""
                raise ex
            return test_function_wrapper
        
        else:
            raise ValueError("Decorated object is neither a class nor a function")
    
    return decorate