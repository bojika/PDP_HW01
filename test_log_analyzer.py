import unittest
import tempfile
import shutil

from log_analyzer import *
import os


class MyTestCase_01(unittest.TestCase):
    def setUp(self):
        self.config_01 = {'a': 1, 'b': 3}
        self.config_02 = {'a': 2}

    def test_merge_config_01(self):
        config = merge_config(internal_config=self.config_01, external_config=self.config_02)
        self.assertEqual(config, {'a': 2, 'b': 3})

    def test_merge_config_02(self):
        config = merge_config(internal_config=self.config_02, external_config=self.config_01)
        self.assertEqual(config, {'a': 1, 'b': 3})


class MyTestCase_02(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        with open(os.path.join(self.tempdir, 'nginx-access-ui.log-20170630.gz'), 'w') as f:
            f.write('Create a new text file!')
        with open(os.path.join(self.tempdir, 'nginx-access-ui.log-20170630'), 'w') as f:
            f.write('Create a new text file!')

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_find_latest_log_01(self):
        lst = ['path', 'date', 'extension']
        Result = namedtuple('Result', lst)
        self.assertEqual(Result(os.path.join(self.tempdir, 'nginx-access-ui.log-20170630'),
                                '2017.06.30',
                                None),
                         find_latest_log(self.tempdir, pattern_for_log_filename))

    def test_find_latest_log_02(self):
        lst = ['path', 'date', 'extension']
        Result = namedtuple('Result', lst)
        with open(os.path.join(self.tempdir, 'nginx-access-ui.log-20170730.gz'), 'w') as f:
            f.write('Create a new text file!')
        self.assertEqual(Result(os.path.join(self.tempdir, 'nginx-access-ui.log-20170730.gz'),
                                '2017.07.30',
                                '.gz'),
                         find_latest_log(self.tempdir, pattern_for_log_filename))

    def test_find_latest_log_03(self):
        lst = ['path', 'date', 'extension']
        Result = namedtuple('Result', lst)
        with open(os.path.join(self.tempdir, 'nginx-access-ui.log-20170730.gz'), 'w') as f:
            f.write('Create a new text file!')
        with open(os.path.join(self.tempdir, 'nginx-access-ui.log-20170730.gz2'), 'w') as f:
            f.write('Create a new text file!')
        self.assertEqual(Result(os.path.join(self.tempdir, 'nginx-access-ui.log-20170730.gz'),
                                '2017.07.30',
                                '.gz'),
                         find_latest_log(self.tempdir, pattern_for_log_filename))


if __name__ == '__main__':
    unittest.main()
