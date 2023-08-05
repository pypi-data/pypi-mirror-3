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
from rhinoplasty.wrapper import wrap_test_function
from rhinoplasty.wrapper import wrap_fixture_with_exception
import inspect


@nottest
def broken_test(item_number, reason):
    """Decorator to mark that this test function or test class is broken.
    
    @param item_number: Item number for the related defect in the issue tracker.
    @param reason: Brief description of why the test is failing.
    @see BrokenTestException for further information on usage.
    """
    return wrap_fixture_with_exception(BrokenTestException(item_number, reason))


@nottest
def broken_inherited_tests(item_number, reason, *functions):
    """Decorator to mark that some test cases inherited from a superclass
    are broken.
    
    @param item_number: Item number for the related defect in the issue tracker.
    @param reason: Brief description of why the test is failing.
    @param functions: List of function names, provided as additional arguments
        to the decorator.
    @see BrokenTestException for further information on usage.
    """
    def decorate(TestClass):
        # Sanity checks
        if not inspect.isclass(TestClass):
            raise TypeError("@failing_virtual_tests must be applied to a class")
        
        if isinstance(item_number, basestring) and \
                hasattr(TestClass, item_number):
            raise ValueError("Defect item number appears to actually be a method: %s" % item_number)
        
        if hasattr(TestClass, reason):
            raise ValueError("Failure reason appears to actually be a method: %s" % reason)
        
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
            @broken_test(item_number, reason)
            @wrap_test_function(original_function)
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
        decorate = wrap_fixture_with_exception(IrrelevantTestException(description))
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
    func = wrap_fixture_with_exception(NotImplementedError(description))
    
    # Decorate the fixture
    if arg_is_fixture:
        return func(arg)
    return func



