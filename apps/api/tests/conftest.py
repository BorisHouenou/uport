"""Pytest configuration for API unit tests.

Adds apps/api to sys.path so schema/model imports resolve correctly,
without contaminating with packages/roo-engine/models.py.
"""
import sys
import os

# Insert at position 0 so apps/api/models/ (package) wins over
# packages/roo-engine/models.py (plain file) in all api tests.
_api_root = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _api_root not in sys.path:
    sys.path.insert(0, _api_root)
