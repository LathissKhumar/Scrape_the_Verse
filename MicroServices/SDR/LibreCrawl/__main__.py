"""
Entry point for python -m LibreCrawl
"""

import sys
import os

# Ensure package is on sys.path
package_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(package_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
if package_dir not in sys.path:
    sys.path.insert(0, package_dir)

from LibreCrawl.cli import main

if __name__ == "__main__":
    sys.exit(main())
