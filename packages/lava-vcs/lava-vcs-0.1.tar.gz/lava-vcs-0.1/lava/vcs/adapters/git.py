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


class _GitBranchMixIn(CommonBranchMixIn):

    @property
    def vcs_name(self):
        return "git"


class GitLocalBranch(_GitBranchMixIn, ILocalBranch):

    def __init__(self, pathname):
        _GitBranchMixIn.__init__(self, pathname)

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
                self.pathname, ".git"))

    def get_revision_id(self):
        proc = self._run_tool_cmd([
            "show",
            # As for '-s': this option is not documented but apparently it
            # prevents git from printing the patch associated with this commit.
            # (I know that git stores the whole object, whatever :P). This
            # option is used in the examples section of: git show --help
            "-s",
            # Display the unabbreviated commit hash
            "--format=%H",
            "HEAD"])
        revision_id = proc.stdout.strip()
        return revision_id

    @property
    def is_dirty(self):
        proc = self._run_tool_cmd(
            ["status", "--porcelain"])
        return proc.stdout != "" or proc.stderr != ""

    def pristinize(self):
        self._run_tool_cmd(
            ["reset", "--quiet", "--hard"])
        # -x has no long form, it removes all files (both ignored and not)
        self._run_tool_cmd(
            ["clean", "--force", "--quiet", "-x"])

    def sprout_to_pathname(self, pathname):
        branch = GitLocalBranch(pathname)
        self._run_tool_cmd(
            ["clone", "--quiet", self.pathname, branch.pathname],
            out_of_tree=True)
        return branch

    def pull_without_merge(self, remote_branch):
        if not isinstance(remote_branch, _GitBranchMixIn):
            raise IncompatibleBranch()
        proc = self._run_tool_cmd(
            ["pull", "--quiet", "--ff-only", remote_branch.location],
            cannot_fail=False)
        if "Not possible to fast-forward" in proc.stderr:
            raise BranchHasDiverged()
        if proc.returncode != 0:
            self._raise_vcs_fault(proc)

    def count_patches_between(self, from_revision_id, to_revision_id):
        proc = self._run_tool_cmd(
            ["log", "--full-history", "--oneline", 
             "%s..%s" % (from_revision_id or "", to_revision_id or "HEAD")],
            cannot_fail=False)
        # XXX: 0, 1 and 2 are valid return values, I checked the source code
        # directly, this was not documented in the man page.
        if proc.returncode not in [0, 1, 2]:
            self._raise_vcs_fault(proc)
        return proc.stdout.count("\n")

    def count_unmerged_patches(self, other_branch):
        if not isinstance(other_branch, _GitBranchMixIn):
            raise IncompatibleBranch()
        # XXX: This is a little ugly
        # XXX: This does not seem to catch file removals :/
        # 1) Add a remote to be able to look at the other branch
        helper_name = 'lava-dev-tool-cherry-helper'
        self._run_tool_cmd(
            ["remote", "add", helper_name, other_branch.location]) 
        self._run_tool_cmd(
            ["fetch", helper_name])
        try:
            # 2a) Run git cherry against master our-special-remote
            proc = self._run_tool_cmd(
                ["cherry", "origin/master", helper_name + "/master"])
            # Count + and - symbols
            missing_there = missing_here = 0
            for line in proc.stdout.split('\n'):
                if line.startswith('+'):
                    missing_there += 1
                elif line.startswith('-'):
                    missing_here += 1
        finally:
            # 3) Remove our helper remote
            self._run_tool_cmd(
                ["remote", "rm",  helper_name])
        return missing_here, missing_there


class GitRemoteBranch(_GitBranchMixIn, IRemoteBranch):

    def __init__(self, url):
        _GitBranchMixIn.__init__(self, url)

    @property
    def is_remote(self):
        return True 

    @property
    def url(self):
        return self._location

    def sprout_to_pathname(self, pathname):
        branch = GitLocalBranch(pathname)
        self._run_tool_cmd(
            ["clone", "--quiet", self.location, branch.location])
        return branch


class Git(IVCS):

    def open_local(self, pathname):
        return GitLocalBranch(pathname)

    def open_remote(self, url):
        return GitRemoteBranch(url)
