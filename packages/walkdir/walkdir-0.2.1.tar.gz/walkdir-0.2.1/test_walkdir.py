#!/usr/bin/env python
"""test_walkdir - unittests for the walkdir module"""
import unittest
import os.path

from walkdir import (include_dirs, exclude_dirs, include_files, exclude_files,
                     limit_depth, min_depth, handle_symlink_loops,
                     filtered_walk, all_paths, dir_paths, file_paths,
                     iter_paths, iter_dir_paths, iter_file_paths)

expected_files = "file1.txt file2.txt other.txt".split()

def fake_walk():
    subdirs = "subdir1 subdir2 other".split()
    files = expected_files
    root_dir = "root"
    yield root_dir, subdirs, files[:]
    for subdir in subdirs:
        dirname = os.path.join(root_dir, subdir)
        subdirs2 = subdirs[:]
        yield dirname, subdirs2, files[:]
        for subdir2 in subdirs2: 
            dirname2 = os.path.join(dirname, subdir2)
            yield dirname2, [], files[:]

expected_tree = [
    ('root', ['subdir1', 'subdir2', 'other'], ['file1.txt', 'file2.txt', 'other.txt']),
    ('root/subdir1', ['subdir1', 'subdir2', 'other'], ['file1.txt', 'file2.txt', 'other.txt']),
    ('root/subdir1/subdir1', [], ['file1.txt', 'file2.txt', 'other.txt']),
    ('root/subdir1/subdir2', [], ['file1.txt', 'file2.txt', 'other.txt']),
    ('root/subdir1/other', [], ['file1.txt', 'file2.txt', 'other.txt']),
    ('root/subdir2', ['subdir1', 'subdir2', 'other'], ['file1.txt', 'file2.txt', 'other.txt']),
    ('root/subdir2/subdir1', [], ['file1.txt', 'file2.txt', 'other.txt']),
    ('root/subdir2/subdir2', [], ['file1.txt', 'file2.txt', 'other.txt']),
    ('root/subdir2/other', [], ['file1.txt', 'file2.txt', 'other.txt']),
    ('root/other', ['subdir1', 'subdir2', 'other'], ['file1.txt', 'file2.txt', 'other.txt']),
    ('root/other/subdir1', [], ['file1.txt', 'file2.txt', 'other.txt']),
    ('root/other/subdir2', [], ['file1.txt', 'file2.txt', 'other.txt']),
    ('root/other/other', [], ['file1.txt', 'file2.txt', 'other.txt']),
]

depth_0_tree = [
    ('root', [], ['file1.txt', 'file2.txt', 'other.txt']),
]

depth_1_tree = [
    ('root', ['subdir1', 'subdir2', 'other'], ['file1.txt', 'file2.txt', 'other.txt']),
    ('root/subdir1', [], ['file1.txt', 'file2.txt', 'other.txt']),
    ('root/subdir2', [], ['file1.txt', 'file2.txt', 'other.txt']),
    ('root/other', [], ['file1.txt', 'file2.txt', 'other.txt']),
]

min_depth_2_tree = [
    ('root/subdir1/subdir1', [], ['file1.txt', 'file2.txt', 'other.txt']),
    ('root/subdir1/subdir2', [], ['file1.txt', 'file2.txt', 'other.txt']),
    ('root/subdir1/other', [], ['file1.txt', 'file2.txt', 'other.txt']),
    ('root/subdir2/subdir1', [], ['file1.txt', 'file2.txt', 'other.txt']),
    ('root/subdir2/subdir2', [], ['file1.txt', 'file2.txt', 'other.txt']),
    ('root/subdir2/other', [], ['file1.txt', 'file2.txt', 'other.txt']),
    ('root/other/subdir1', [], ['file1.txt', 'file2.txt', 'other.txt']),
    ('root/other/subdir2', [], ['file1.txt', 'file2.txt', 'other.txt']),
    ('root/other/other', [], ['file1.txt', 'file2.txt', 'other.txt']),
]

dir_filtered_tree = [
    ('root', ['subdir1'], ['file1.txt', 'file2.txt', 'other.txt']),
    ('root/subdir1', ['subdir1'], ['file1.txt', 'file2.txt', 'other.txt']),
    ('root/subdir1/subdir1', [], ['file1.txt', 'file2.txt', 'other.txt']),
]

expected_paths = [
'root',
'root/file1.txt',
'root/file2.txt',
'root/other.txt',
'root/subdir1',
'root/subdir1/file1.txt',
'root/subdir1/file2.txt',
'root/subdir1/other.txt',
'root/subdir1/subdir1',
'root/subdir1/subdir1/file1.txt',
'root/subdir1/subdir1/file2.txt',
'root/subdir1/subdir1/other.txt',
'root/subdir1/subdir2',
'root/subdir1/subdir2/file1.txt',
'root/subdir1/subdir2/file2.txt',
'root/subdir1/subdir2/other.txt',
'root/subdir1/other',
'root/subdir1/other/file1.txt',
'root/subdir1/other/file2.txt',
'root/subdir1/other/other.txt',
'root/subdir2',
'root/subdir2/file1.txt',
'root/subdir2/file2.txt',
'root/subdir2/other.txt',
'root/subdir2/subdir1',
'root/subdir2/subdir1/file1.txt',
'root/subdir2/subdir1/file2.txt',
'root/subdir2/subdir1/other.txt',
'root/subdir2/subdir2',
'root/subdir2/subdir2/file1.txt',
'root/subdir2/subdir2/file2.txt',
'root/subdir2/subdir2/other.txt',
'root/subdir2/other',
'root/subdir2/other/file1.txt',
'root/subdir2/other/file2.txt',
'root/subdir2/other/other.txt',
'root/other',
'root/other/file1.txt',
'root/other/file2.txt',
'root/other/other.txt',
'root/other/subdir1',
'root/other/subdir1/file1.txt',
'root/other/subdir1/file2.txt',
'root/other/subdir1/other.txt',
'root/other/subdir2',
'root/other/subdir2/file1.txt',
'root/other/subdir2/file2.txt',
'root/other/subdir2/other.txt',
'root/other/other',
'root/other/other/file1.txt',
'root/other/other/file2.txt',
'root/other/other/other.txt'
]

expected_dir_paths = [d for d in expected_paths if not d.endswith('.txt')]
expected_file_paths = [f for f in expected_paths if f.endswith('.txt')]

depth_0_paths = [
'root',
'root/file1.txt',
'root/file2.txt',
'root/other.txt',
]

depth_0_dir_paths = [d for d in depth_0_paths if not d.endswith('.txt')]
depth_0_file_paths = [f for f in depth_0_paths if f.endswith('.txt')]

filtered_paths = [
'root',
'root/file1.txt',
'root/subdir1',
'root/subdir1/file1.txt',
'root/subdir1/subdir1',
'root/subdir1/subdir1/file1.txt',
]

filtered_dir_paths = [d for d in filtered_paths if not d.endswith('.txt')]
filtered_file_paths = [f for f in filtered_paths if f.endswith('.txt')]


class _BaseWalkTestCase(unittest.TestCase):
    # XXX: "actual, expected" would be a more typical order for the arguments
    def assertWalkEqual(self, expected, walk_iter):
        return self.assertEqual(expected, list(walk_iter))

class NoFilesystemTestCase(_BaseWalkTestCase):
    
    # Sanity check on the test data generator
    def test_fake_walk(self):
        self.assertWalkEqual(expected_tree, fake_walk())

    def test_limit_depth(self):
        self.assertWalkEqual(depth_0_tree, limit_depth(fake_walk(), 0))
        self.assertWalkEqual(depth_1_tree, limit_depth(fake_walk(), 1))
        
    def test_min_depth(self):
        self.assertWalkEqual([], min_depth(fake_walk(), 4))
        self.assertWalkEqual(expected_tree[1:], min_depth(fake_walk(), 1))
        self.assertWalkEqual(min_depth_2_tree, min_depth(fake_walk(), 2))
        
    def test_include_dirs(self):
        self.assertWalkEqual(depth_0_tree, include_dirs(fake_walk()))
        self.assertWalkEqual(expected_tree, include_dirs(fake_walk(), '*'))
        self.assertWalkEqual(expected_tree, include_dirs(fake_walk(), 'sub*', 'other'))

    def test_exclude_dirs(self):
        self.assertWalkEqual(expected_tree, exclude_dirs(fake_walk()))
        self.assertWalkEqual(depth_0_tree, exclude_dirs(fake_walk(), '*'))
        self.assertWalkEqual(depth_0_tree, exclude_dirs(fake_walk(), 'sub*', 'other'))

    def test_filter_dirs(self):
        walk_iter = include_dirs(fake_walk(), 'sub*')
        walk_iter = exclude_dirs(walk_iter, '*2')
        self.assertWalkEqual(dir_filtered_tree, walk_iter)

    def test_filter_dirs_with_min_depth(self):
        walk_iter = include_dirs(fake_walk(), 'sub*')
        walk_iter = exclude_dirs(walk_iter, '*2')
        walk_iter = min_depth(walk_iter, 1)
        self.assertWalkEqual(dir_filtered_tree[1:], walk_iter)

    def test_include_files(self):
        for dirname, subdirs, files in include_files(fake_walk()):
            self.assertEqual(files, [])
        for dirname, subdirs, files in include_files(fake_walk(), '*'):
            self.assertEqual(files, expected_files)
        for dirname, subdirs, files in include_files(fake_walk(), 'file*', 'other*'):
            self.assertEqual(files, expected_files)
        for dirname, subdirs, files in include_files(fake_walk(), 'file*'):
            self.assertEqual(files, ['file1.txt', 'file2.txt'])

    def test_exclude_files(self):
        for dirname, subdirs, files in exclude_files(fake_walk()):
            self.assertEqual(files, expected_files)
        for dirname, subdirs, files in exclude_files(fake_walk(), '*'):
            self.assertEqual(files, [])
        for dirname, subdirs, files in exclude_files(fake_walk(), 'file*', 'other*'):
            self.assertEqual(files, [])
        for dirname, subdirs, files in exclude_files(fake_walk(), 'file*'):
            self.assertEqual(files, ['other.txt'])

    def test_filter_files(self):
        walk_iter = include_files(fake_walk(), 'file*')
        walk_iter = exclude_files(walk_iter, '*2*')
        for dirname, subdirs, files in walk_iter:
            self.assertEqual(files, ['file1.txt'])

    def test_legacy_names(self):
        self.assertIs(iter_paths, all_paths)
        self.assertIs(iter_dir_paths, dir_paths)
        self.assertIs(iter_file_paths, file_paths)


class FilteredWalkTestCase(_BaseWalkTestCase):
    # Basically repeat all the standalone cases via the convenience API
    def fake_walk(self, *args, **kwds):
        return filtered_walk(fake_walk(), *args, **kwds)

    def test_unfiltered(self):
        self.assertWalkEqual(expected_tree, filtered_walk(fake_walk()))

    def test_limit_depth(self):
        self.assertWalkEqual(depth_0_tree, self.fake_walk(depth=0))
        self.assertWalkEqual(depth_1_tree, self.fake_walk(depth=1))
        
    def test_min_depth(self):
        self.assertWalkEqual([], self.fake_walk(min_depth=4))
        self.assertWalkEqual(expected_tree[1:], self.fake_walk(min_depth=1))
        self.assertWalkEqual(min_depth_2_tree, self.fake_walk(min_depth=2))
        
    def test_include_dirs(self):
        self.assertWalkEqual(depth_0_tree, self.fake_walk(included_dirs=()))
        self.assertWalkEqual(expected_tree, self.fake_walk(included_dirs=['*']))
        self.assertWalkEqual(expected_tree, self.fake_walk(included_dirs=['sub*', 'other']))

    def test_exclude_dirs(self):
        self.assertWalkEqual(expected_tree, self.fake_walk(excluded_dirs=()))
        self.assertWalkEqual(depth_0_tree, self.fake_walk(excluded_dirs=['*']))
        self.assertWalkEqual(depth_0_tree, self.fake_walk(excluded_dirs=['sub*', 'other']))

    def test_filter_dirs(self):
        walk_iter = self.fake_walk(included_dirs=['sub*'],
                                   excluded_dirs=['*2'])
        self.assertWalkEqual(dir_filtered_tree, walk_iter)

    def test_include_files(self):
        for dirname, subdirs, files in self.fake_walk(included_files=()):
            self.assertEqual(files, [])
        for dirname, subdirs, files in self.fake_walk(included_files=['*']):
            self.assertEqual(files, expected_files)
        for dirname, subdirs, files in self.fake_walk(included_files=['file*', 'other*']):
            self.assertEqual(files, expected_files)
        for dirname, subdirs, files in self.fake_walk(included_files=['file*']):
            self.assertEqual(files, ['file1.txt', 'file2.txt'])

    def test_exclude_files(self):
        for dirname, subdirs, files in self.fake_walk(excluded_files=()):
            self.assertEqual(files, expected_files)
        for dirname, subdirs, files in self.fake_walk(excluded_files=['*']):
            self.assertEqual(files, [])
        for dirname, subdirs, files in self.fake_walk(excluded_files=['file*', 'other*']):
            self.assertEqual(files, [])
        for dirname, subdirs, files in self.fake_walk(excluded_files=['file*']):
            self.assertEqual(files, ['other.txt'])

    def test_filter_files(self):
        walk_iter = self.fake_walk(included_files=['file*'],
                                   excluded_files=['*2*'])
        for dirname, subdirs, files in walk_iter:
            self.assertEqual(files, ['file1.txt'])

class PathIterationTestCase(_BaseWalkTestCase):
    def fake_walk(self, *args, **kwds):
        return filtered_walk(fake_walk(), *args, **kwds)

    def test_all_paths(self):
        self.assertWalkEqual(expected_paths, all_paths(self.fake_walk()))
        self.assertWalkEqual(expected_paths[len(depth_0_paths):],
                             all_paths(self.fake_walk(min_depth=1)))
        self.assertWalkEqual(depth_0_paths, all_paths(self.fake_walk(depth=0)))
        walk_iter = self.fake_walk(included_files=['file*'],
                                   excluded_files=['*2*'],
                                   included_dirs=['sub*'],
                                   excluded_dirs=['*2'],)
        self.assertWalkEqual(filtered_paths, all_paths(walk_iter))

    def test_dir_paths(self):
        self.assertWalkEqual(expected_dir_paths, dir_paths(self.fake_walk()))
        self.assertWalkEqual(expected_dir_paths[len(depth_0_dir_paths):],
                             dir_paths(self.fake_walk(min_depth=1)))
        self.assertWalkEqual(depth_0_dir_paths, dir_paths(self.fake_walk(depth=0)))
        walk_iter = self.fake_walk(included_files=['file*'],
                                   excluded_files=['*2*'],
                                   included_dirs=['sub*'],
                                   excluded_dirs=['*2'])
        self.assertWalkEqual(filtered_dir_paths, dir_paths(walk_iter))

    def test_file_paths(self):
        self.assertWalkEqual(expected_file_paths, file_paths(self.fake_walk()))
        self.assertWalkEqual(expected_file_paths[len(depth_0_file_paths):],
                             file_paths(self.fake_walk(min_depth=1)))
        self.assertWalkEqual(depth_0_file_paths, file_paths(self.fake_walk(depth=0)))
        walk_iter = self.fake_walk(included_files=['file*'],
                                   excluded_files=['*2*'],
                                   included_dirs=['sub*'],
                                   excluded_dirs=['*2'])
        self.assertWalkEqual(filtered_file_paths, file_paths(walk_iter))
        

# TODO: Create filesystem in temporary directory, add tests for 'handle_symlink_loops'

if __name__ == "__main__":
    unittest.main()
