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

from testtools.helpers import map_values
from testtools.matchers import (
    ContainsDict,
    Equals,
    Matcher,
    MatchesDict,
    )

from ._treeshape import (
    load_tree,
    )


def add_implicit_directories(shape):
    """
    Take a normalized shape and make sure all parent directories are included
    in it.
    """
    new_shape = dict(shape)
    # XXX: This is really slow.  We could do something better, especially
    # given that shape is sorted by name.
    for name in shape:
        for parent in iterate_parents(name):
            if parent not in new_shape:
                new_shape[parent] = {}
    return new_shape


def iterate_parents(path):
    path = path.rstrip(os.sep)
    while True:
        path = os.path.dirname(path)
        if not path:
            break
        yield path + '/'


def _is_matcher(value):
    return isinstance(value, Matcher)


def _to_matcher(value, default_matcher=Equals):
    if _is_matcher(value):
        return value
    return Equals(value)


class MatchesFileTree(Matcher):
    """Match a directory on disk against a file tree shape.

    The specified shape contains everything that is allowed to exist in the
    matched directory.  Parent directories that are implied by actual entries
    (e.g. 'foo/bar/' implies that 'foo/' exists) will be automatically added.

    Attributes can be matched using testtools matchers, e.g.::

      {'foo': {CONTENTS: Contains("Hello")}}

    Or will be simply checked for equality if they aren't matchers.  Thus::

      {'foo': {CONTENTS: Equals("Hello")}}

    is equivalent to::

      {'foo': {CONTENTS: "Hello"}}

    ``from_rough_spec`` also works with matchers, so you could call
    ``MatchesFileTree`` like this, if you want::

        MatchesFileTree(from_rough_spec([('foo', Contains("Hello")), 'bar/']))

    If the disk contains any files or directories that aren't specified in the
    matcher and aren't implied directories, then it will mismatch.  Likewise,
    if there are entries in the matcher spec that don't exist on disk, it will
    mismatch.
    """

    tree_matcher = MatchesDict

    def __init__(self, shape):
        super(MatchesFileTree, self).__init__()
        self.shape = shape

    def _matchify_attributes(self, attrs):
        """Return a matcher that matches disk attributes with expected ones.
        """
        # The pattern is that a user doesn't specify attributes they don't
        # care about.  Thus, we return a ContainsDict matcher.
        return ContainsDict(map_values(_to_matcher, attrs))

    def match(self, path):
        found_shape = load_tree(path)
        expected_shape = add_implicit_directories(self.shape)
        expected_shape = map_values(self._matchify_attributes, expected_shape)
        return self.tree_matcher(expected_shape).match(found_shape)


class HasFileTree(MatchesFileTree):
    """As ``MatchesFileTree`` but OK if some things on disk aren't specified.
    """

    tree_matcher = ContainsDict

