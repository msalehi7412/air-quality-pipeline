# src/tests/conftest.py
import os, sys

# HERE = .../src/tests
HERE = os.path.dirname(__file__)
# SRC  = .../src
SRC  = os.path.abspath(os.path.join(HERE, ".."))
# ROOT = project root (parent of src)
ROOT = os.path.abspath(os.path.join(SRC, ".."))

for p in (SRC, ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)
