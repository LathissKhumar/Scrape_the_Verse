"""
LibreCrawl - Headless SEO Crawling & Audit Engine
Entry point redirecting to the headless CLI / API.
"""

import os
import sys

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
