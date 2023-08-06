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

import os 

from lava.vcs.interface import (
    ILocalBranch,
    IRemoteBranch,
    IVCS,
)
from lava.vcs.errors import (
    BranchHasDiverged,
    IncompatibleBranch,
)
from lava.vcs.adapters.common import CommonBranchMixIn


class _BzrBranchMixIn(CommonBranchMixIn):

    @property
    def vcs_name(self):
        return "bzr"


class BzrLocalBranch(_BzrBranchMixIn, ILocalBranch):

    def __init__(self, pathname):
        _BzrBranchMixIn.__init__(self, pathname)

    @property
    def is_remote(self):
        return False

    @property
    def pathname(self):
        return self.location

    @property
    def exists(self):
        return os.path.exists(
            os.path.join(
                self.pathname, ".bzr"))

    def get_revision_id(self):
        proc = self._run_tool_cmd(["revision-info"])
        if ' ' not in proc.stdout.strip():
            self._raise_vcs_fault(proc)
        revno, revision_id = proc.stdout.strip().split(' ', 1)
        return revision_id

    @property
    def is_dirty(self):
        proc = self._run_tool_cmd(["status"])
        return proc.stdout != "" or proc.stderr != ""

    def pristinize(self):
        self._run_tool_cmd(["revert", "--quiet", "--no-backup"])
        self._run_tool_cmd(["clean-tree", "--force", "--quiet"])
        self._run_tool_cmd(["clean-tree", "--ignored", "--force", "--quiet"])

    def sprout_to_pathname(self, pathname):
        branch = BzrLocalBranch(pathname)
        self._run_tool_cmd(
            ["branch", self.pathname, branch.pathname],
            out_of_tree=True)
        return branch

    def pull_without_merge(self, remote_branch):
        if not isinstance(remote_branch, _BzrBranchMixIn):
            raise IncompatibleBranch()
        proc = self._run_tool_cmd(
            ["pull", "--quiet", remote_branch.location],
            cannot_fail=False)
        if "These branches have diverged." in proc.stderr:
            raise BranchHasDiverged()
        if proc.returncode != 0:
            self._raise_vcs_fault(proc)

    def count_patches_between(self, from_revision_id, to_revision_id):
        command = ["log", "--quiet", "--log-format=line", "--include-merges",
                   "--revision=%s..%s" % (from_revision_id or "", to_revision_id or "")]
        if from_revision_id != to_revision_id:
            command.append("--exclude-common-ancestry")
        proc = self._run_tool_cmd(command)
        # XXX: -1 is becauase bzr uses inclusive ranges
        return proc.stdout.count("\n") - 1

    def count_unmerged_patches(self, other_branch):
        if not isinstance(other_branch, _BzrBranchMixIn):
            raise IncompatibleBranch()
        proc = self._run_tool_cmd(
            ["missing", "--quiet", "--theirs-only", "--log-format=line",
             other_branch.location])
        missing_here = proc.stdout.count("\n")
        proc = self._run_tool_cmd(
            ["missing", "--quiet", "--mine-only", "--log-format=line",
             other_branch.location])
        missing_there = proc.stdout.count("\n")
        return missing_here, missing_there


class BzrRemoteBranch(_BzrBranchMixIn, IRemoteBranch):

    def __init__(self, url):
        _BzrBranchMixIn.__init__(self, url)

    @property
    def is_remote(self):
        return True 

    @property
    def url(self):
        return self._location

    def sprout_to_pathname(self, pathname):
        branch = BzrLocalBranch(pathname)
        self._run_tool_cmd(
            ["branch", "--quiet", self.location, branch.location])
        return branch


class Bzr(IVCS):

    def open_local(self, pathname):
        return BzrLocalBranch(pathname)

    def open_remote(self, url):
        return BzrRemoteBranch(url)
