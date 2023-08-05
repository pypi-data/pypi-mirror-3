"""Nose plugin for displaying results from rich errors."""

from nose.plugins.errorclass import ErrorClass, ErrorClassPlugin
from _errors import *

class RichErrorReportingPlugin(ErrorClassPlugin):
    """Plugin that installs error class handling for all the rich errors
    defined in this package.
    """
    # Standard Plugin attributes
    enabled = False
    name = "rich-errors"
    score = 1001 # Handle errors before the standard Skip plugin #TODO check this works
    
    # Define error classes that we handle
    broken = ErrorClass(BrokenTestException, label='BROKEN', isfailure=True)
    excluded = ErrorClass(ExcludeTestException, label='XCLUDE', isfailure=False) #TODO better label
    misconfigured = ErrorClass(InvalidTestConfigurationException, label='CONFIG_WRONG', isfailure=False) #TODO better label
    irrelevant = ErrorClass(IrrelevantTestException, label='IRRELEVANT', isfailure=False)
    
    # Use default implementation of options() and configure to enable this plugin

