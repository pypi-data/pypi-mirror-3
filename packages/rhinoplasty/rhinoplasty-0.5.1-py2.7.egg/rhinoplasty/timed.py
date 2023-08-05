"""Functions for timing tests."""

from nose.tools import TimeExpired
from threading import Event
from threading import Thread
from .wrapper import wrap_test_function


# Limit A Test's Duration
# -----------------------
def timeboxed(max_time):
    """Decorator to limit how long a test will run for.
    
    @param max_time: The maximum number of seconds the test is allowed to run
        for.
    @raise TimeExpired If the test runs too long. Nose will treat this as a
        test failure, rather than an error.
    @see nose.tools.timed for an alternative approach. The difference is that
        this decorator will not allow the test function to run any longer than
        the specified time limit, whereas Nose's version will wait until the
        test function finishes (however long that takes) before failing.
    """
    #FIXME check max explicitly, rather than waiting for func execution
    
    def decorate(func):
        @wrap_test_function(func)
        def new_func(*args, **kwargs):
            # Create a separate thread to run the function in.
            # 
            # Because we could decorate any arbitrary function, we do not have
            # any control over it's execution. Hence we need to run the
            # function in parallel, so that if it exceeds the allocated time
            # we can abandon it and return from the original thread of
            # execution. 
            # 
            # The multiprocessing module would provide some useful features
            # (such as the ability to terminate the target function if it runs
            # too long), but we can't use it because that would change the
            # execution environment for the target function.
            target = _TimeoutFunctionThread(lambda : func(*args, **kwargs))
            target.start()
            
            # Wait for the target function to finish executing, or else reach
            # it's time limit
            if not target.finished.wait(max_time):
                raise TimeExpired("%s could not be run within %s seconds" % (func.__name__, max_time))
            assert target.finished.is_set()
            
            # Return result for original function
            if target.exception is not None:
                raise target.exception
            return target.result
        
        return new_func
    
    return decorate


# Private Functions
# -----------------
class _TimeoutFunctionThread(Thread):
    """Run a function in a background thread and wait for it to complete..
    
    @param func: A parameter-less function to run.
    @see timeboxed
    """
    
    def __init__(self, func):
        Thread.__init__(self)
        
        # Target function to execute.
        #
        # The default Thread implementation will run a supplied function, but
        # it won't do anything with the result of the function. Hence we need
        # to completely replace this functionality.
        self.target_func = func
        
        # Event that is set when the function has finished executing
        self.finished = Event()
        
        # Result from executing the target function. This is only valid when
        # the function has finished, and if exception is None.
        self.result = None
        
        # Exception raised by the target function (if any). This is only valid
        # when the function has finished.
        self.exception = None
        
        # Mark the thread as daemonic so that the Python process won't wait for
        # an overly long function to finish executing before exiting. This is
        # most relevant for running a single unit test.
        self.daemon = True
    
    def run(self):
        self.finished.clear()
        
        try:
            self.result = self.target_func()
        except Exception, ex:
            self.exception = ex
        
        self.finished.set()
