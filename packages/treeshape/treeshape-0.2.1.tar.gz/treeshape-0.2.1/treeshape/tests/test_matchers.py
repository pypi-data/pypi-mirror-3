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

import stat

from testtools import TestCase
from testtools.matchers import (
    Contains,
    MatchesPredicate,
    )

from treeshape import (
    CONTENT,
    FileTree,
    from_rough_spec,
    HasFileTree,
    MatchesFileTree,
    PERMISSIONS,
    )

from treeshape._matchers import (
    add_implicit_directories,
    iterate_parents,
    )


class TestIterateParents(TestCase):

    def test_single_segment(self):
        self.assertEqual([], list(iterate_parents('foo')))
        self.assertEqual([], list(iterate_parents('foo/')))

    def test_multiple_segments(self):
        self.assertEqual(
            [('foo/bar/'), ('foo/')],
            list(iterate_parents('foo/bar/baz.txt')))
        self.assertEqual(
            [('foo/bar/'), ('foo/')],
            list(iterate_parents('foo/bar/baz/')))


class TestAddImplicitDirectories(TestCase):

    def test_empty(self):
        self.assertEqual({}, add_implicit_directories({}))

    def test_no_implicit_directories(self):
        shape = from_rough_spec([
            'foo',
            'bar/',
            'bar/baz.txt',
            ])
        self.assertEqual(shape, add_implicit_directories(shape))

    def test_implicit_directories(self):
        shape = from_rough_spec([
            'foo',
            'bar/baz.txt',
            'bar/qux/',
            ])
        self.assertEqual(
            {'bar/': {},
             'bar/baz.txt': {},
             'bar/qux/': {},
             'foo': {},
            }, add_implicit_directories(shape))


class TestMatchesFileTree(TestCase):

    def test_empty(self):
        path = self.useFixture(FileTree({})).path
        self.assertThat(path, MatchesFileTree({}))

    def test_missing_file(self):
        path = self.useFixture(FileTree({})).path
        mismatch = MatchesFileTree({'foo': {}}).match(path)
        self.assertIsNot(None, mismatch)

    def test_unexpected_file(self):
        path = self.useFixture(FileTree({'foo': {}, 'bar': {}})).path
        mismatch = MatchesFileTree({'bar': {}}).match(path)
        self.assertIsNot(None, mismatch)

    def test_files_and_directories(self):
        shape = {
            'foo': {CONTENT: 'contents', PERMISSIONS: 0755},
            'bar/': {PERMISSIONS: 0700},
            }
        path = self.useFixture(FileTree(shape)).path
        self.assertThat(path, MatchesFileTree(shape))

    def test_with_matchers(self):
        shape = {
            'foo': {CONTENT: 'contents', PERMISSIONS: 0755},
            'bar/': {PERMISSIONS: 0400},
            }
        path = self.useFixture(FileTree(shape)).path
        is_user_readable = MatchesPredicate(
            lambda p: p & stat.S_IRUSR, "User can't read: %s")
        self.assertThat(
            path, MatchesFileTree(
                {'foo': {CONTENT: Contains('on')},
                 'bar/': {PERMISSIONS: is_user_readable}}))

    def test_unspecified_permissions(self):
        shape = {
            'foo': {CONTENT: 'contents'},
            'bar/': {},
            }
        path = self.useFixture(FileTree(shape)).path
        self.assertThat(path, MatchesFileTree(shape))

    def test_unspecified_contents(self):
        shape = {'foo': {}, 'bar/': {}}
        path = self.useFixture(FileTree(shape)).path
        self.assertThat(path, MatchesFileTree(shape))

    def test_implicit_directories(self):
        shape = {'foo/bar/': {}, 'foo/bar.txt': {}}
        path = self.useFixture(FileTree(shape)).path
        self.assertThat(path, MatchesFileTree(shape))

    def test_with_dwim(self):
        shape = {
            'foo': {CONTENT: 'contents', PERMISSIONS: 0755},
            'bar/': {PERMISSIONS: 0700},
            }
        path = self.useFixture(FileTree(shape)).path
        expected = [
            ('foo', Contains('on')),
            'bar/',
            ]
        self.assertThat(path, MatchesFileTree(from_rough_spec(expected)))


class TestHasFileTree(TestCase):

    def test_unexpected_file(self):
        path = self.useFixture(FileTree({'foo': {}, 'bar': {}})).path
        self.assertThat(path, HasFileTree({'bar': {}}))
