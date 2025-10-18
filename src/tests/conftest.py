# src/tests/conftest.py
import os, sys

# HERE = .../src/tests
HERE = os.path.dirname(__file__)
# SRC = .../src
SRC = os.path.abspath(os.path.join(HERE, ".."))

if SRC not in sys.path:
    sys.path.insert(0, SRC)
