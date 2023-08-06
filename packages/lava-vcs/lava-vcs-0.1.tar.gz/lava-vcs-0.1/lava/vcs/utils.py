# Copyright (C) 2010, 2011 Linaro Limited
#
# Author: Zygmunt Krynicki <zygmunt.krynicki@linaro.org>
#
# This file is part of lava-vcs.
#
# lava-vcs is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License version 3
# as published by the Free Software Foundation
#
# lava-vcs is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with lava-vcs.  If not, see <http://www.gnu.org/licenses/>.

"""
Generic utilities
"""
import logging
import os
import pkg_resources


def mkdir_p(path):
    """
    Equivalent of mkdir -p.

    Needed because os.makedirs() sucks and fails to work in the most common
    situation when you need it to.
    """
    if not os.path.exists(path):
        os.makedirs(path)


class EntryPointResolver(object):
    """
    Helper for resolving entry points by name.
    """

    def __init__(self, namespace):
        """
        Create a resolved that looks at the specified namespace.
        """
        self.namespace = namespace
        self._cache = {}

    def resolve(self, name):
        """
        Resolve an entry point by name.

        Any ImportError exceptions are logged but otherwise ignored. If
        multiple entry points with the same name exist the first one to be
        returned by pkg_resources wins.

        :return None if the item is not found
        :return The, possibly cached, entry point if found
        """
        if name in self._cache:
            return self._cache[name]
        vcs = self._resolve(name)
        self._cache[name] = vcs
        return vcs

    def _resolve(self, name):
        for entry_point in pkg_resources.iter_entry_points(self.namespace):
            if entry_point.name != name:
                continue
            try:
                return entry_point.load()
            except ImportError:
                logging.exception("Unable to import entry point %s",
                                  entry_point)
