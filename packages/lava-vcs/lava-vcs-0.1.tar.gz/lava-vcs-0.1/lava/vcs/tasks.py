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

from celery.decorators import task

from lava.vcs.adapters import get_vcs
from lava.vcs.errors import BranchHasDiverged 


@task(name="Clone remote repository")
def clone_remote(vcs_name, remote_url, local_path):
    """
    Clone a remote branch to a local path
    """
    vcs = get_vcs(vcs_name)
    remote_branch = vcs.open_remote(remote_url)
    local_branch = remote_branch.sprout_to_pathname(local_path)


@task(name="Update local repository")
def update_local(vcs_name, remote_url, local_path):
    """
    Update existing branch by doing fast-forward pull from a remote branch

    :return Number of patches pulled
    :raises BranchHasDiverged: if the operation is not possible
    """
    vcs = get_vcs(vcs_name)
    local_branch = vcs.open_local(local_path)
    start_rev = local_branch.get_revision_id()
    remote_branch = vcs.open_remote(remote_url)
    end_rev = local_branch.get_revision_id()
    local_branch.pull_without_merge(remote_branch)
    return local_branch.count_patches_between(start_rev, end_rev)
