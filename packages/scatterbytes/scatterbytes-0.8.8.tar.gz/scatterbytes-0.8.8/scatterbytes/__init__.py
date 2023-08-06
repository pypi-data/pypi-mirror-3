
__version__ = '0.8.8'

import logging

# used for server logging
logging.addLevelName(19, 'REQUEST')

# Clean up namespace.
del logging 


