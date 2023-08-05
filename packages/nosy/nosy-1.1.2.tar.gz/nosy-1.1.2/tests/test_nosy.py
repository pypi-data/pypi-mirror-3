"""Unit tests for nosy.
"""
from __future__ import absolute_import
from mock import Mock
import os
from tempfile import NamedTemporaryFile
try:
    import unittest2 as unittest
except ImportError:
    import unittest


class TestNosy(unittest.TestCase):
    """Unit tests for Nosy.
    """
    def _get_target_class(self):
        from nosy.nosy import Nosy
        return Nosy


    def _make_one(self, *args, **kwargs):
        return self._get_target_class()(*args, **kwargs)


    def test_extra_paths_empty(self):
        """Zero checksum when extra_paths is empty
        """
        nosy = self._make_one()
        nosy.extra_paths = []
        nosy.paths = []  # backward compatibility for 1.0
        checksum = nosy._calc_extra_paths_checksum()
        self.assertEqual(checksum, 0)


    def test_extra_paths_checksum(self):
        """Non-zero checksum when extra_paths is not empty
        """
        nosy = self._make_one()
        tmp_file = NamedTemporaryFile()
        nosy.extra_paths = [tmp_file.name]
        nosy.paths = []  # backward compatibility for 1.0
        checksum = nosy._calc_extra_paths_checksum()
        self.assertNotEqual(checksum, 0)


    def test_extra_paths_checksum_changes(self):
        """Extra paths checksum changes when file is touched
        """
        nosy = self._make_one()
        tmp_file = NamedTemporaryFile()
        nosy.extra_paths = [tmp_file.name]
        nosy.paths = []  # backward compatibility for 1.0
        checksum1 = nosy._calc_extra_paths_checksum()
        tmp_file.write('foobar')
        tmp_file.flush()
        checksum2 = nosy._calc_extra_paths_checksum()
        self.assertNotEqual(checksum1, checksum2)


    def test_exclude_patterns_empty(self):
        """Empty exclusions set when exclude_patterns is empty
        """
        nosy = self._make_one()
        nosy.exclude_patterns = []
        exclusions = nosy._calc_exclusions('.')
        self.assertItemsEqual(exclusions, set())


    def test_exclude_patterns(self):
        """Expected exclusions set when exclude_patterns is not empty
        """
        nosy = self._make_one()
        nosy.exclude_patterns = ['*.py']
        exclusions = nosy._calc_exclusions('./nosy')
        self.assertItemsEqual(
            exclusions, set(['./nosy/__init__.py', './nosy/nosy.py']))


    def test_dir_checksum_glob_patterns_empty(self):
        """Zero checksum when glob_patterns is empty
        """
        nosy = self._make_one()
        nosy.glob_patterns = []
        checksum = nosy._calc_dir_checksum([], '.')
        self.assertEqual(checksum, 0)


    def test_dir_checksum_glob_patterns_no_match(self):
        """Zero checksum when glob pattern doesn't match
        """
        nosy = self._make_one()
        nosy.glob_patterns = ['zzz*']
        tmp_file = NamedTemporaryFile()
        root = os.path.dirname(tmp_file.name)
        checksum = nosy._calc_dir_checksum([], root)
        self.assertEqual(checksum, 0)


    def test_dir_checksum_glob_patterns_match(self):
        """Non-zero checksum when file matching glob pattern exists in dir
        """
        nosy = self._make_one()
        nosy.glob_patterns = ['tmp*']
        tmp_file = NamedTemporaryFile()
        root = os.path.dirname(tmp_file.name)
        checksum = nosy._calc_dir_checksum([], root)
        self.assertNotEqual(checksum, 0)


    def test_dir_checksum_changes(self):
        """Checksum changes when file is touched
        """
        nosy = self._make_one()
        nosy.glob_patterns = ['tmp*']
        tmp_file = NamedTemporaryFile()
        root = os.path.dirname(tmp_file.name)
        checksum1 = nosy._calc_dir_checksum([], root)
        tmp_file.write('foobar')
        tmp_file.flush()
        checksum2 = nosy._calc_dir_checksum([], root)
        self.assertNotEqual(checksum1, checksum2)


    def test_dir_checksum_changes_when_file_excluded(self):
        """Checksum changes when a file is excluded
        """
        nosy = self._make_one()
        nosy.glob_patterns = ['tmp*']
        tmp_file1 = NamedTemporaryFile()
        tmp_file2 = NamedTemporaryFile()
        root = os.path.dirname(tmp_file1.name)
        checksum1 = nosy._calc_dir_checksum([], root)
        checksum2 = nosy._calc_dir_checksum([tmp_file2.name], root)
        self.assertNotEqual(checksum1, checksum2)


    def test_checksum_method_calls(self):
        """Number of calls & args from _checksum is as expected
        """
        nosy = self._make_one()
        nosy.base_path = './nosy'
        nosy._calc_extra_paths_checksum = Mock(return_value=0)
        nosy._calc_exclusions = Mock(return_value=[])
        nosy._calc_dir_checksum = Mock(return_value=0)
        nosy._checksum()
        nosy._calc_extra_paths_checksum.assert_called_once()
        nosy._calc_exclusions.assert_called_once_with('./nosy')
        nosy._calc_dir_checksum.assert_called_once_with([], './nosy')
