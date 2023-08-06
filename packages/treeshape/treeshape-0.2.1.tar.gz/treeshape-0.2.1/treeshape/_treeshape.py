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

"""Support for making and reading "tree shapes".

A "tree shape" is a dict mapping names of files and directories to attributes,
where "attributes" are dicts that contain keys like ``CONTENT`` or
``PERMISSIONS`` that describe the file or directory.

In a tree shape, if a key ends with a '/', then it's a directory.  Otherwise,
it's a file.
"""

import errno
import os


# This is what the standard library uses for the default mode passed to
# os.makedirs.
DEFAULT_MODE = 0777

CONTENT = 'content'
PERMISSIONS = 'permissions'


class InvalidDirectory(ValueError):
    """Raised when we are given a confusing directory description."""

    def __init__(self, entry):
        super(InvalidDirectory, self).__init__(
            "Directories must end with '/' and have no content, got %r"
            % (entry,))


def validate_entry(name, attributes, original=None):
    is_dir = (name[-1] == '/')
    if is_dir:
        if attributes.get(CONTENT, None) is not None:
            if not original:
                original = (name, attributes)
            raise InvalidDirectory(original)


def make_tree(base_directory, shape, mode=DEFAULT_MODE):
    """Make a tree of files and directories underneath ``base_directory``.

    :param shape: A dict of descriptions of files and directories to make.
        The name of the file or directory to create is the key.  If you want
        to create a directory, make sure the name ends with '/'.

        The value is a dict.  Recognized keys are ``PERMISSIONS``, which if
        provided will be used to set the file system permissions for the
        created directory, and ``CONTENT``, which if provided for a file
        will be the contents of that file.

    :raise InvalidDirectory: if a directory has a ``CONTENT`` key.
    """
    for name, attributes in sorted(shape.items()):
        if not attributes:
            attributes = {}
        path = os.path.join(base_directory, name)
        validate_entry(name, attributes)
        if name[-1] == '/':
            os.makedirs(path, mode)
        else:
            base_dir = os.path.dirname(path)
            try:
                os.makedirs(base_dir, mode)
            except OSError, e:
                if e.errno != errno.EEXIST:
                    raise
            contents = attributes.get(CONTENT, "The file '%s'." % (name,))
            f = open(path, 'w')
            f.write(contents)
            f.close()
        permissions = attributes.get(PERMISSIONS)
        if permissions:
            os.chmod(path, permissions)


def _get_permissions(path):
    """Get the permissions of ``path``.

    Much like os.stat(path).st_mode, except we only preserve the last four
    octal digits.  Thus, it returns things like 0755 rather than 0100755.
    """
    return int(oct(os.stat(path).st_mode)[-4:], 8)


def _get_info(dirpath, name, directory):
    path = os.path.join(dirpath, name)
    name = os.path.relpath(path, directory)
    permissions = _get_permissions(path)
    return path, name, permissions


def load_tree(directory):
    """Return a tree shape corresponding to the files beneath ``directory``.

    :param directory: A directory on disk.
    :raises ValueError: If ``directory`` points to a non-directory.
    :return: a tree shape of all files and directories beneath ``directory``.
    """
    if not os.path.isdir(directory):
        raise ValueError(
            "Can only load tree for directories, got %r" % (directory,))
    shape = {}
    for dirpath, dirnames, filenames in os.walk(directory):
        for name in dirnames:
            path, name, permissions = _get_info(dirpath, name, directory)
            shape[name + '/'] = {PERMISSIONS: permissions}
        for name in filenames:
            path, name, permissions = _get_info(dirpath, name, directory)
            content = open(path, 'rb').read()
            shape[name] = {CONTENT: content, PERMISSIONS: permissions}
    return shape
