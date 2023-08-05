"""Nose plugin for displaying results from rich errors."""

from nose.plugins.errorclass import ErrorClass, ErrorClassPlugin
from _errors import *
import inspect
import logging

logger = logging.getLogger("rhinoplasty.rich_errors")

class RichErrorReportingPlugin(ErrorClassPlugin):
    """Nose plugin that installs error output handling for a richer error set
    (as described elsewhere in this package).
    """
    # Standard Plugin attributes
    name = "rich-errors"
    
    # Define error classes that we handle
    #TODO Be able to customise the single letter labels
    broken = ErrorClass(BrokenTestException, label='BROKEN', isfailure=False) #TODO should this be a failure? If so, we want to stop displaying tracebacks for it.
    excluded = ErrorClass(ExcludeTestException, label='XCLUDE', isfailure=False) #TODO better label
    irrelevant = ErrorClass(IrrelevantTestException, label='IRRELEVANT', isfailure=False)
    misconfigured = ErrorClass(InvalidTestConfigurationException, label='CONFIG_WRONG', isfailure=True) #TODO better label
    transient = ErrorClass(TransientTestError, label="TRANSIENT", isfailure=False)
    unimplemented = ErrorClass(NotImplementedError, label="UNIMPLEMENTED", isfailure=False) #TODO should this be a failure? If so, we want to stop displaying tracebacks for it.
    
    # Use default implementation of options() and configure to enable this plugin
    def configure(self, options, conf):
        super(RichErrorReportingPlugin, self).configure(options, conf)
        
        if self.enabled:
            # The xunit plugin only has limited categories for errors, and
            # does not provide any method to configure it's behaviour.
            #
            # Therefore we monkey patch the xunit plugin so that it reports our
            # non-failure exceptions as skip's. The easiest way to achieve this
            # is to change SkipTest to be a tuple of skippable error types, so
            # that the issubclass test in Xunit.addError will return True.
            #
            # Note that this is *extremely* dodgy.
            from nose.plugins import xunit
            
            if inspect.isclass(xunit.SkipTest):
                logger.info("Monkey patching xunit plugin to recognise rich errors...")
                new_skips = [xunit.SkipTest]
                for cls, (name, label, isfailure) in self.errorClasses:
                    if not isfailure:
                        new_skips.append(cls)
                
                xunit.SkipTest = tuple(new_skips)
            else:
                logger.warn("Unable to monkey-patch xunit plugin, since it's " \
                            "SkipTest definition has an unexpected type: %s",
                            xunit.SkipTest)
    
    def help(self):
        return "Display richer error types."

