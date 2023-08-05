"""Additional exceptions for working with automated tests."""

#TODO new error for when the functionality is not yet implemented (although the tests are written).
    # -> just use NotImplementedError in the code, and handle that specifically
    # Add an alias (or decorator) here to make this clearer? SubjectUnderTestNotImplementedException

#FIXME update docstring for SkipTest to label it as abstract and general ???


__all__ = [
    'BrokenTestException',
    'ExcludeTestException',
    'InvalidTestConfigurationException',
    'IrrelevantTestException',
]


from nose.plugins.skip import SkipTest


class BrokenTestException(SkipTest):
    """Skip a test because it is known to be broken.
    
    This avoids constantly re-running tests that are known to fail or cause an
    error, yet allows us to still mark them as failures.
    
    In a perfect Test Driven Development world, all broken tests would be
    fixed immediately by the developer that caused them to break.
    
    However, test frameworks are not necessarily used in a perfect TDD world
    (for instance, consider a situation where tests are being written against
    an existing legacy codebase), so pragmatically we need some process to
    manage the broken tests.
    
    Some example scenarios:
     * The development team decide that the defect exposed by the test can be
        tolerated in the short-term, but will allocate resources to fix it in
        the long-term.
     * It is not known how to fix the defect exposed by the test.
     * The defect exposed by the test is caused by a third party product.
     * The defect exposed by the test cannot be fixed without making
        incompatible changes to the product's external API (and these changes
        need to be carefully managed).
    
    This differs from the standard unittest.expectedFailure decorator in that
    it does not attempt to run the test. It is also more flexible
    (expectedFailure can only be applied to functions as a decorator), and
    there is support for it in Nose.
    """
    pass


class ExcludeTestException(SkipTest):
    """Skip a test because the user specifically excluded it from the current
    test run.
    
    This differs from the standard unittest.SkipTest exception in that it is
    specifically intended for exclusions specified at test-run-time, whereas
    SkipTest has a very general meaning and implies nothing about the reason
    for skipping the test.
    
    Note that there may be other ways to exclude unwanted tests (eg. Nose
    provides several ways to specify which functions should be considered as
    tests).
    """
    pass


class InvalidTestConfigurationException(SkipTest):
    """Skip a test because the system is not configured correctly.
    
    For example, this might be used when a test fixture cannot be setup because
    important configuration information (such as the database to connect to)
    has not been supplied by the user. 
    
    This situation should be considered a test failure.
    """
    #TODO review all uses of this exception to ensure they are appropriate (eg. some might need to be ExcludeTestException, or a different sort of error)
    pass


class IrrelevantTestException(SkipTest):
    """Skip a test because it is not relevant for the current system.
    
    For example, this might be used to avoid running a Linux-specific test
    under Microsoft Windows.
    """
    pass
