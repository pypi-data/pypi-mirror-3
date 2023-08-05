"""Decorators for applying rich exceptions."""

__all__ = [
    'broken_inherited_tests',
    'broken_test',
    'irrelevant_test',
    'unimplemented_subject_under_test',
]


from _errors import BrokenTestException
from _errors import IrrelevantTestException
from nose.tools import nottest
from rhinoplasty.wrapper import wrap_test_fixture
import inspect


@nottest
def broken_test(arg):
    """Decorator to mark that this test function or test class is broken.
    
    This decorator may be used without arguments, or else it accepts a single
    string argument describing why the test fails.
    
    @see BrokenTestException for further information on usage.
    """
    # Allow for two different decoration options
    arg_is_fixture = True
    description = "Test is known to fail"
    
    if isinstance(arg, basestring):
        description = arg
        arg_is_fixture = False
    
    # Get the wrapper function for the test fixture
    func = _decorate_fixture(description, BrokenTestException)
    
    # Decorate the fixture
    if arg_is_fixture:
        return func(arg)
    return func


@nottest
def broken_inherited_tests(reason, *functions):
    """Decorator to mark that some test cases inherited from a superclass
    are broken.
    
    @param reason: Description of why the test is failing.
    @param functions: List of function names, provided as additional arguments
        to the decorator.
    @see BrokenTestException for further information on usage.
    """
    def decorate(TestClass):
        # Sanity checks
        if not inspect.isclass(TestClass):
            raise TypeError("@failing_virtual_tests must be applied to a class")
        
        if hasattr(TestClass, reason):
            raise ValueError("Failure reason appears to actually be a method: '%s'" % reason)
        
        # Mark these tests for this subclass only.
        # The only way to do this is to overwrite the method on the subclass,
        # and mark the overwritten method as a failure.
        for funcname in functions:
            # Check that we have a reference to a valid superclass method
            for SuperClass in inspect.getmro(TestClass):
                if hasattr(SuperClass, funcname):
                    original_function = getattr(SuperClass, funcname)
                    break
            else:
                raise ValueError("Test method '%s' is not defined by any superclass of %s" % (funcname, TestClass))
            
            # Create a replacement function
            @broken_test(reason)
            @wrap_test_fixture(original_function)
            def new_method(self):
                bound_function = original_function.__get__(self, TestClass)
                bound_function()
            
            setattr(TestClass, funcname, new_method)
        
        return TestClass
    
    return decorate


@nottest
def irrelevant_test(condition, description):
    """Decorator to mark that this test function or test class is irrelevant
    in some situations.
    
    @param condition: Boolean condition describing whether the test is
        irrelevant. 
    @param description: Describes why the test is irrelevant.
    @see IrrelevantTestException for further information on usage.
    """
    assert (isinstance(description, basestring)), "Description is not a string - check that the parameters are correct"
    
    if condition:
        # Skip the test fixture
        decorate = _decorate_fixture(description, IrrelevantTestException)
    else:
        # Leave the decorated fixture unchanged.
        def decorate(fixture):
            return fixture
    
    return decorate


@nottest
def unimplemented_subject_under_test(arg):
    """Decorator to mark that this test function or test class is broken
    because the functionality under test has not been implemented.
    
    Alternatively, the test may raise NotImplementedError directly, and it will
    be treated exactly the same.
    
    This decorator may be used without arguments, or else it accepts a single
    string argument describing the functionality that is not implemented.
    
    @see BrokenTestException for further information on usage.
    """
    # Allow for two different decoration options
    arg_is_fixture = True
    description = "Subject Under Test is not yet implemented"
    
    if isinstance(arg, basestring):
        description = arg
        arg_is_fixture = False
    
    # Get the wrapper function for the test fixture
    func = _decorate_fixture(description, NotImplementedError)
    
    # Decorate the fixture
    if arg_is_fixture:
        return func(arg)
    return func


@nottest
def _decorate_fixture(description, ExceptionClass):
    """Get a decorator wrapper function for a test fixture, that will raise an
    exception when the tests are run.
    
    @param description: Description for why the decorated object is skipped.
    @param ExceptionClass: The exception class to raise.
    """
    #TODO should we move this function to the wrapper module?
    def decorate(fixture):
        if inspect.isclass(fixture):
            # Create a replacement class that raises an appropriate exception
            @wrap_test_fixture(fixture)
            class ClassWrapper(object):
                def test_suite_raises_exception(self):
                    raise ExceptionClass(description)
                test_suite_raises_exception.__doc__ = fixture.__doc__
            
            return ClassWrapper
                    
        elif callable(fixture):
            # Create a replacement function that raises an appropriate exception
            
            #noinspection PyUnusedLocal
            @wrap_test_fixture(fixture)
            def function_wrapper(*args):
                """Replaces the failing test and unconditionally raises an exception."""
                raise ExceptionClass(description)
            return function_wrapper
        else:
            raise ValueError("Decorated object is neither a class nor a function")
    
    return decorate
