"""module Exceptions.

"""
# Standard library imports
import logging

# Third party imports
from odoo.exceptions import ValidationError

# Local application imports

# CONSTANTS

# Module init variables
_logger = logging.getLogger(__name__)


class BaseModuleNameError(ValidationError):
    pass
