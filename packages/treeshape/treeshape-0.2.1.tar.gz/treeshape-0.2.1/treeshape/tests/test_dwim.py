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

from testtools import TestCase
from testtools.matchers import Is

from treeshape import (
    CONTENT,
    DuplicateName,
    from_rough_spec,
    InvalidDirectory,
    PERMISSIONS,
    )
from treeshape._dwim import (
    _from_rough_entry,
    )


class TestNormalizeEntry(TestCase):

    def test_file_as_tuple(self):
        # A tuple of filenames and contents is not quite normalized. It still
        # needs 'None' added to the end, to represent default permissions.
        entry = _from_rough_entry(('foo', 'foo contents'))
        self.assertEqual(('foo', {CONTENT: 'foo contents'}), entry)

    def test_file_with_permissions_as_tuple(self):
        # A tuple of filename, contents and permissions is already normalized.
        entry = _from_rough_entry(('foo', 'foo contents', 0755))
        self.assertEqual(
            ('foo', {CONTENT: 'foo contents', PERMISSIONS: 0755}), entry)

    def test_directories_as_tuples(self):
        # A tuple of directory name and None is not quite normalized. It still
        # needs 'None' added to the end, to represent default permissions.
        directory = _from_rough_entry(('foo/', None))
        self.assertEqual(('foo/', {}), directory)

    def test_directories_with_permissions_as_tuples(self):
        # A tuple of directory name, None and None is already normalized.
        directory = _from_rough_entry(('foo/', None, None))
        self.assertEqual(('foo/', {}), directory)

    def test_directories_as_singletons(self):
        # A singleton tuple of directory name is normalized to a 2-tuple of
        # the directory name and None.
        directory = _from_rough_entry(('foo/',))
        self.assertEqual(('foo/', {}), directory)

    def test_directories_as_strings(self):
        # If directories are just given as strings, then they are normalized
        # to tuples of directory names and None.
        directory = _from_rough_entry('foo/')
        self.assertEqual(('foo/', {}), directory)

    def test_directories_with_content(self):
        # If we're given a directory with content, we raise an error, since
        # it's ambiguous and we don't want to guess.
        bad_entry = ('dir/', "stuff")
        e = self.assertRaises(InvalidDirectory, _from_rough_entry, bad_entry)
        self.assertEqual(
            "Directories must end with '/' and have no content, got %r"
            % (bad_entry,), str(e))

    def test_directories_with_permissions(self):
        entry = ('dir/', 0755)
        self.assertEqual(
            ('dir/', {PERMISSIONS: 0755}), _from_rough_entry(entry))

    def test_directories_with_content_and_empty_permissions(self):
        # If we're given a directory with content, we raise an error, since
        # it's ambiguous and we don't want to guess.
        bad_entry = ('dir/', "stuff", None)
        e = self.assertRaises(InvalidDirectory, _from_rough_entry, bad_entry)
        self.assertEqual(
            "Directories must end with '/' and have no content, got %r"
            % (bad_entry,), str(e))

    def test_directories_with_content_and_permissions(self):
        # If we're given a directory with content, we raise an error, since
        # it's ambiguous and we don't want to guess.
        bad_entry = ('dir/', "stuff", 0755)
        e = self.assertRaises(InvalidDirectory, _from_rough_entry, bad_entry)
        self.assertEqual(
            "Directories must end with '/' and have no content, got %r"
            % (bad_entry,),
            str(e))

    def test_filenames_as_strings(self):
        # If file names are just given as strings, then they are normalized to
        # tuples of filenames and made-up contents.
        entry = _from_rough_entry('foo')
        self.assertEqual(('foo', {}), entry)

    def test_filenames_as_singletons(self):
        # A singleton tuple of a filename is normalized to a 2-tuple of
        # the file name and made-up contents.
        entry = _from_rough_entry(('foo',))
        self.assertEqual(('foo', {}), entry)

    def test_filenames_without_content(self):
        # If we're given a filename without content, make something up.
        entry = ('foo', None)
        self.assertEqual(('foo', {}), _from_rough_entry(entry))

    def test_filenames_without_content_with_empty_permissions(self):
        # If we're given a filename without content, we raise an error, since
        # it's ambiguous and we don't want to guess.
        entry = ('filename', None, None)
        self.assertEqual(('filename', {}), _from_rough_entry(entry))

    def test_filenames_with_just_permission(self):
        # If we're given a filename without content, we raise an error, since
        # it's ambiguous and we don't want to guess.
        entry = ('filename', 0755)
        self.assertEqual(
            ('filename', {PERMISSIONS: 0755}), _from_rough_entry(entry))

    def test_filenames_without_content_with_permissions(self):
        # If we're given a filename without content, and we are also given
        # permissions, well then we're honour-bound to create the file.
        entry = ('filename', None, 0755)
        self.assertEqual(
            ('filename', {PERMISSIONS: 0755}), _from_rough_entry(entry))

    def test_too_long_tuple(self):
        bad_entry = ('foo', 'bar', 'baz', 'qux')
        e = self.assertRaises(ValueError, _from_rough_entry, bad_entry)
        self.assertEqual(
            "Invalid file or directory description: %r" % (bad_entry,),
            str(e))

    def test_passes_matchers_through(self):
        marker = object()
        entry = ('filename', Is(marker))
        name, attributes = _from_rough_entry(entry)
        self.assertEqual('filename', name)
        self.assertEqual([CONTENT], attributes.keys())
        self.assertThat(marker, attributes[CONTENT])


class TestFromRoughSpec(TestCase):

    def test_empty(self):
        self.assertEqual({}, from_rough_spec([]))

    def test_dict_of_normalized_entries(self):
        entries = ['filename', ('dir/', 0755)]
        normalized_entries = [('filename', {}), ('dir/', {PERMISSIONS: 0755})]
        self.assertEqual(dict(normalized_entries), from_rough_spec(entries))

    def test_duplicate_name(self):
        entries = ['a', 'a']
        self.assertRaises(DuplicateName, from_rough_spec, entries)
