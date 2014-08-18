import unittest
import gns3converter


class TestVersion(unittest.TestCase):
    def test_version(self):
        self.assertEqual(gns3converter.__version__, '0.1.1')

if __name__ == '__main__':
    unittest.main()
