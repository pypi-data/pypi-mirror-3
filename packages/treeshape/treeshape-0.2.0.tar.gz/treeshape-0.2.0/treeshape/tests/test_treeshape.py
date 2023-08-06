#  treeshape: quickly make file and directory structures.
#
# Copyright (c) 2012, Jonathan Lange <jml@mumak.net>
#
# Licensed under either the Apache License, Version 2.0 or the BSD 3-clause
# license at the users choice. A copy of both licenses are available in the
# project source as Apache-2.0 and BSD. You may not use this file except in
# compliance with one of these two licences.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under these licenses is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
# license you chose for the specific language governing permissions and
# limitations under that license.

import os

from fixtures import TempDir

import testtools
from testtools.matchers import (
    DirContains,
    DirExists,
    Equals,
    FileContains,
    HasPermissions,
    )

from treeshape._treeshape import (
    DEFAULT_MODE,
    load_tree,
    )
from treeshape import (
    CONTENT,
    FileTree,
    InvalidDirectory,
    make_tree,
    PERMISSIONS,
    )


class TestMakeTree(testtools.TestCase):

    def test_directory_and_subdirectory(self):
        # If both a directory and a sub-directory are explicitly listed,
        # that's OK.
        path = self.useFixture(TempDir()).path
        make_tree(path, {'a/b/': {}, 'a/': {}})
        self.assertThat(path, DirContains(['a']))
        self.assertThat(os.path.join(path, 'a'), DirContains(['b']))
        self.assertThat(os.path.join(path, 'a', 'b'), DirExists())

    def test_empty(self):
        tempdir = self.useFixture(TempDir()).path
        make_tree(tempdir, {})
        self.assertThat(tempdir, DirContains([]))

    def test_creates_files(self):
        # When given file specifications, it creates those files underneath
        # the temporary directory.
        path = self.useFixture(TempDir()).path
        make_tree(path, {'a': {CONTENT: 'foo'}, 'b': {CONTENT: 'bar'}})
        self.assertThat(path, DirContains(['a', 'b']))
        self.assertThat(os.path.join(path, 'a'), FileContains('foo'))
        self.assertThat(os.path.join(path, 'b'), FileContains('bar'))

    def test_creates_directories(self):
        # When given directory specifications, it creates those directories.
        path = self.useFixture(TempDir()).path
        make_tree(path, {'a/': {}, 'b/': {}})
        self.assertThat(path, DirContains(['a', 'b']))
        self.assertThat(os.path.join(path, 'a'), DirExists())
        self.assertThat(os.path.join(path, 'b'), DirExists())

    def test_any_false_will_do(self):
        # If the attributes of the file is None, or an empty list or whatever,
        # treat it like an empty dict.
        path = self.useFixture(TempDir()).path
        make_tree(path, {'a/b/': None, 'c/d.txt': False})
        self.assertThat(path, DirContains(['a', 'c']))
        self.assertThat(os.path.join(path, 'a'), DirContains('b'))
        self.assertThat(os.path.join(path, 'a', 'b'), DirExists())
        self.assertThat(os.path.join(path, 'c'), DirExists())
        self.assertThat(
            os.path.join(path, 'c', 'd.txt'),
            FileContains("The file 'c/d.txt'."))

    def test_creates_parent_directories(self):
        # If the parents of a file or directory don't exist, they get created
        # too.
        path = self.useFixture(TempDir()).path
        make_tree(path, {'a/b/': {}, 'c/d.txt': {CONTENT: 'text'}})
        self.assertThat(path, DirContains(['a', 'c']))
        self.assertThat(os.path.join(path, 'a'), DirContains('b'))
        self.assertThat(os.path.join(path, 'a', 'b'), DirExists())
        self.assertThat(os.path.join(path, 'c'), DirExists())
        self.assertThat(os.path.join(path, 'c', 'd.txt'), FileContains('text'))

    def test_sets_permissions(self):
        path = self.useFixture(TempDir()).path
        make_tree(
            path, {
                'a/b/': {PERMISSIONS: 0755},
                'c/d.txt': {CONTENT: 'text', PERMISSIONS: 0600},
                })
        self.assertThat(os.path.join(path, 'a/b/'), HasPermissions('0755'))
        self.assertThat(os.path.join(path, 'c/d.txt'), HasPermissions('0600'))

    def test_directory_contents(self):
        # If CONTENT is passed to a directory, it raises InvalidDirectory.
        path = self.useFixture(TempDir()).path
        self.assertRaises(
            InvalidDirectory,
            make_tree, path, {'a/': {CONTENT: 'ignored'}})

    def test_mode(self):
        # 'mode' can be optionally passed in.  Used for implicitly created
        # directories.
        path = self.useFixture(TempDir()).path
        make_tree(
            path, {
                'a/b/': {PERMISSIONS: 0755},
                'c/d.txt': {CONTENT: 'text', PERMISSIONS: 0600}
                },
            mode=0700)
        self.assertThat(os.path.join(path, 'a/'), HasPermissions('0700'))
        self.assertThat(os.path.join(path, 'a/b/'), HasPermissions('0755'))
        self.assertThat(os.path.join(path, 'c/'), HasPermissions('0700'))


class TestLoadTree(testtools.TestCase):

    def load_tree_from(self, input_shape, mode=DEFAULT_MODE):
        path = self.useFixture(FileTree(input_shape, mode)).path
        return load_tree(path)

    def test_empty(self):
        self.assertThat(self.load_tree_from({}), Equals({}))

    def test_single_file(self):
        shape = {'foo': {CONTENT: 'content', PERMISSIONS: 0755}}
        found_shape = self.load_tree_from(shape)
        self.assertThat(found_shape, Equals(shape))

    def test_directories(self):
        shape = {'foo/': {PERMISSIONS: 0755}}
        found_shape = self.load_tree_from(shape)
        self.assertThat(found_shape, Equals(shape))

    def test_subdirectories(self):
        shape = {
            'foo/bar/': {PERMISSIONS: 0755},
            'foo/baz.txt': {CONTENT: 'content', PERMISSIONS: 0755},
            }
        found_shape = self.load_tree_from(shape, mode=0700)
        self.assertThat(
            found_shape,
            Equals(
                {'foo/': {PERMISSIONS: 0700},
                 'foo/bar/': {PERMISSIONS: 0755},
                 'foo/baz.txt': {CONTENT: 'content', PERMISSIONS: 0755},
                 }))

    def test_not_a_directory(self):
        path = self.useFixture(FileTree({'foo.txt': {}})).path
        path = os.path.join(path, 'foo.txt')
        e = self.assertRaises(ValueError, load_tree, path)
        self.assertEqual(
            "Can only load tree for directories, got %r" % (path,), str(e))
