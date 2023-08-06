"""
A python library to do development based in Finite State Machines.
"""
from ginsfsm.gaplic import GAplic
from ginsfsm.gobj import GObj
from ginsfsm.smachine import SMachine

# Set default logging handler to avoid "No handler found" warnings.
import logging
try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())

# ... Clean up.
del logging
del NullHandler
