"""Communication Service Package."""

import os
import sys

# Ensure this service directory is in sys.path
_service_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _service_dir not in sys.path:
    sys.path.insert(0, _service_dir)

__version__ = "1.0.0"
