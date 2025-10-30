"""WSGI shim that re-exports the real application.

Some deployment configurations reference `thirdyear.thirdyear.wsgi:application`.
This module forwards that to the real `thirdyear.wsgi.application`.
"""
from ..wsgi import application  # re-export
