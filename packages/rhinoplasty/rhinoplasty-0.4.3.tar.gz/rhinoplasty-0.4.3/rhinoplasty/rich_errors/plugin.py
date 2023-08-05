"""Nose plugin for displaying results from rich errors."""

from nose.plugins.errorclass import ErrorClass, ErrorClassPlugin
from _errors import *

class RichErrorReportingPlugin(ErrorClassPlugin):
    """Nose plugin that installs error output handling for a richer error set
    (as described elsewhere in this package).
    """
    # Standard Plugin attributes
    name = "rich-errors"
    
    # Define error classes that we handle
    broken = ErrorClass(BrokenTestException, label='BROKEN', isfailure=True)
    excluded = ErrorClass(ExcludeTestException, label='XCLUDE', isfailure=False) #TODO better label; be able to customise the shortcut letter?
    misconfigured = ErrorClass(InvalidTestConfigurationException, label='CONFIG_WRONG', isfailure=False) #TODO better label
    irrelevant = ErrorClass(IrrelevantTestException, label='IRRELEVANT', isfailure=False)
    
    # Use default implementation of options() and configure to enable this plugin
    
    def help(self):
        return "Display richer error types."

