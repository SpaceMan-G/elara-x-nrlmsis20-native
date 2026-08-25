import unittest
import elara_x_nrlmsis20 as package

class PackageImportTests(unittest.TestCase):
    def test_public_surface(self):
        for name in ('initialize', 'is_initialized', 'calculate', 'gtd8d'):
            self.assertTrue(callable(getattr(package, name)))

if __name__ == '__main__':
    unittest.main()
