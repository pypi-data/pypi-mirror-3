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

from lava_server.extension import LavaServerExtension


class VCSExtension(LavaServerExtension):
    """
    Extension adding vcs support
    """

    @property
    def app_name(self):
        return "lava.vcs"

    @property
    def name(self):
        return "VCS"

    @property
    def main_view_name(self):
        return "lava.vcs.index"

    @property
    def description(self):
        return "VCS support for LAVA"

    @property
    def version(self):
        import lava.vcs
        import versiontools
        return versiontools.format_version(
            lava.vcs.__version__, hint=lava.vcs)
