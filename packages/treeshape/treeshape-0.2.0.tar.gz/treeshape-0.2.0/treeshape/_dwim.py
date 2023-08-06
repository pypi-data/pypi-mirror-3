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


from ._treeshape import (
    CONTENT,
    PERMISSIONS,
    validate_entry,
    )


def _is_permission(possible_permissions):
    """Is ``possible_permissions`` a permission?"""
    return isinstance(possible_permissions, int)


def _guess_content_or_permissions(content_or_permissions):
    """
    Given a thing that could be either content or permissions, guess which it
    is.

    Used when we are given a 2-tuple to figure out what the second element of
    the tuple actually is.
    """
    if content_or_permissions is None:
        return {}
    elif _is_permission(content_or_permissions):
        return {PERMISSIONS: content_or_permissions}
    else:
        return {CONTENT: content_or_permissions}


def _normalize_entry(entry):
    if isinstance(entry, basestring):
        return (entry, {})

    if len(entry) == 1:
        return (entry[0], {})

    if len(entry) == 2:
        name, content_or_permissions = entry
        attributes = _guess_content_or_permissions(content_or_permissions)
        return name, attributes

    if len(entry) == 3:
        name, content, permissions = entry
        attributes = {}
        if content:
            attributes[CONTENT] = content
        if permissions:
            attributes[PERMISSIONS] = permissions
        return name, attributes

    raise ValueError(
        "Invalid file or directory description: %r" % (entry,))


def _from_rough_entry(entry):
    """Normalize a file shape entry.

    'Normal' entries are ("file": {CONTENT: "content"}), ("directory/",
    {PERMISSIONS: 0755}) and so forth.  They have a name and attributes.

    Standalone strings get turned into normal entries with no attributes.
    Singleton tuples are treated the same.

    If something looks like a directory and has content, we raise an error, as
    we don't know whether the developer really intends a file or really
    intends a directory.

    :raise ValueError: If we're given a tuple that's too long, or that we
        can't understand.
    :raise InvalidDirectory: If we're given a directory description with file
        content.  What's that even supposed to mean?
    :return: A 2-tuple of name and attributes. Attributes might contain
        CONTENT or PERMISSIONS.
    """
    name, attributes = _normalize_entry(entry)
    validate_entry(name, attributes, entry)
    return name, attributes


class DuplicateName(Exception):

    def __init__(self, first, second):
        super(DuplicateName, self).__init__(
            "Duplicate name given.  Did you mean %r or did you mean %r?"
            % (first, second))
        self.first = first
        self.second = second


def from_rough_spec(list_shape):
    """Create a tree shape from a list of rough specifications.

    Rather than fully and explicitly specifying a tree shape,
    ``from_rough_spec`` allows you to say things like::

      dwim(['filename', ('directory/', 0755), ('data', 'content goes here')])

    And have that turned into a proper tree shape::

      {'filename': {},
       'directory/': {PERMISSIONS: 0755},
       'data': {CONTENT: 'content goes here'}}

    Use this when you wish to be succinct.

    Consider this a "Do What I Mean" (DWIM) function, with all the pros and
    cons that entails.

    :raises DuplicateName: If the same name is given more than once.
    :raises ValueError: If any of the specifications are too long, or
        we simply cannot understand.
    :raises InvalidDirectory: If a specification looks like it's for a
        directory, but has content.  What's that even supposed to mean?
    :return: A dict mapping names to attributes.
    """
    shape = {}
    for entry in list_shape:
        name, attributes = _from_rough_entry(entry)
        if name in shape:
            raise DuplicateName((name, shape[name]), entry)
        shape[name] = attributes
    return shape
