def load_tests(loader, standard_tests, pattern):
    import doctest
    import os
    import sys
    import unittest
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    suite.addTest(loader.loadTestsFromName(__name__))
    source_readme_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "README")
    if os.path.exists(source_readme_path):
        suite.addTest(
            doctest.DocFileTest(os.path.relpath(
                    source_readme_path, os.path.dirname(__file__)),
                optionflags=doctest.NORMALIZE_WHITESPACE))
    else:
        sys.stderr.write("Warning: not testing README as it can't be found")
    return suite

