"""Detailed error classes that allow more fine-grained control over skipped
tests, by specifying the intention of the skip.

This package includes:
 * New rich error classes (available by importing the package).
 * Decorators for applying the errors (available by importing the package).
 * Nose Plugin for handling the errors (automatically installed by setup tools).
"""

from _decorators import *
from _errors import *

#TODO tests (?)