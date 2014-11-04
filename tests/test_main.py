import unittest
from gns3converter.main import snapshot_name
from gns3converter.converterror import ConvertError


class TestMain(unittest.TestCase):
    def test_snapshot_name(self):
        res = snapshot_name('/home/daniel/GNS3/Projects/snapshot_test/'
                            'snapshots/topology_Begin_snapshot_250814_140731/'
                            'topology.net')

        self.assertEqual(res, 'Begin_250814_140731')
        # assertRaises(excClass, callableObj, args)
        self.assertRaises(ConvertError, snapshot_name, '')
