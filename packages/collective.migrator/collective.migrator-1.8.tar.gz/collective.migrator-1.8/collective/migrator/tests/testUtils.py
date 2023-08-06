import unittest
import os
from collective.migrator.recipes import utils

class TestUtils(unittest.TestCase):

    def setUp(self):
        os.system('mkdir /tmp/test123')

    def test_copy_file(self):
        # make sure the shuffled sequence does not lose any elements
        source = {}
        target = {}
        source['host'] = 'localhost'
        target['host'] = 'localhost'
        source_dir = '/tmp'
        target_dir = '/tmp/test123'
        file_name = 'test1.tmp'
        os.system('touch /tmp/test1.tmp')
        utils.copy_file(source, source_dir, file_name, target, target_dir, keep=True)

        # check file
        self.assertTrue(os.access('/tmp/test123/test1.tmp', os.F_OK))
        self.assertTrue(os.access('/tmp/test1.tmp', os.F_OK))

        os.remove('/tmp/test123/test1.tmp')

    def test_copy_file2(self):
        source = {}
        target = {}
        source['host'] = 'localhost'
        target['host'] = 'localhost'
        source_dir = '/tmp'
        target_dir = '/tmp/test123'
        file_name = 'test1.tmp'
        utils.copy_file(source, source_dir, file_name, target, target_dir, keep=False)

        # check file
        self.assertTrue(os.access('/tmp/test123/test1.tmp', os.F_OK))
        self.assertFalse(os.access('/tmp/test1.tmp', os.F_OK))

        os.remove('/tmp/test123/test1.tmp')

    def tearDown(self):
        os.system('rmdir /tmp/test123')

if __name__ == '__main__':
    unittest.main()


