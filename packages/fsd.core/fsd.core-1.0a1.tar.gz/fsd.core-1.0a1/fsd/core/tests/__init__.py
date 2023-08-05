import sys
try:
    import unittest2 as unittest
except ImportError:
    if sys.version_info >= (2, 7):
        import unittest
    else:
        raise RuntimeError("unittest2 or Python >=2.7 is required "
                           "to perform these tests.")
