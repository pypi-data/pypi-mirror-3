import unittest

def test_suite():
    module_names = [
        'oops_celery.tests.test_oops_reporter',
        ]
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromNames(module_names)
    return suite
