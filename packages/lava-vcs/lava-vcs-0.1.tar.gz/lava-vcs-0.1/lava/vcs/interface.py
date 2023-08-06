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
Interface classes and extension points for public-facing APIs
"""

from abc import ABCMeta, abstractmethod, abstractproperty


class Interface(object):
    """
    Interface class that simply uses the ABCMeta meta-class
    """

    __metaclass__ = ABCMeta


class IBranch(Interface):
    """
    Abstraction of a branch
    """

    @abstractproperty
    def location(self):
        """
        The version-control specific location of this branch.
        """

    @abstractproperty
    def is_remote(self):
        """
        True if this branch is remote
        """

    @abstractproperty
    def vcs_name(self):
        """
        Name of the version control system used by this branch
        """


class ILocalBranch(IBranch):
    """
    Abstraction of a version branch that exists as a standalone directory on
    the local filesystem.

    This is not able to cover _all_ the possible things that people refer to as
    branch. It roughly represents a Bazaar branch or Git repository and the
    master branch inside.
    """

    @abstractproperty
    def pathname(self):
        """
        Pathname on the local filesystem
        """

    @abstractproperty
    def exists(self):
        """
        True if the branch currently exists
        """

    @abstractmethod
    def get_revision_id(self):
        """
        Return the identifier of the top of the branch

        :raises VCSFailure: when there is some other problem with the VCS.
        """

    @abstractmethod
    def is_dirty(self):
        """
        Check if the branch has uncommitted changes that are not ignored.

        :return True if the branch is not pristine
        :raises VCSFailure: when there is some other problem with the VCS.
        """

    @abstractmethod
    def pristinize(self):
        """
        Remove all the uncommitted changes, including all the files that are
        ignored but are present in the tree.
        
        This is equivalent to:

            bzr revert && bzr clean-tree && bzr clean-tree --ignored 
        """

    @abstractmethod
    def sprout_to_pathname(self, pathname):
        """
        Create a local branch from the copy of the remote branch an its current
        state.

        :return Locally created Branch
        :raises VCSFailure: when there is some other problem with the VCS.
        """

    @abstractmethod
    def pull_without_merge(self, remote_branch):
        """
        Pull all the revisions from remote branch if it can be done so by the
        means of git fast forward of bzr pull.

        :raises BranchHasDiverged: if the operation is not possible.
        :raises IncompatibleBranch: when other_branch is using a foreign VCS.
        :raises VCSFailure: when there is some other problem with the VCS.
        """

    @abstractmethod
    def count_patches_between(self, from_revision_id, to_revision_id):
        """
        Count the number of patches between two revisions present in this
        branch. Either revision may be None, in which case it represents the
        first and last revision respectively.

        :return number of patches between the two revisions
        :raises VCSFailure: when there is some other problem with the VCS.
        """

    @abstractmethod
    def count_unmerged_patches(self, other_branch):
        """
        Count the number of patches that exist in this branch but not merged in
        other branch (and vice versa but this is not symmetric).

        :return tuple of integers (missing_here, missing_there)
        :raises IncompatibleBranch: when other_branch is using a foreign VCS.
        :raises VCSFailure: when there is some other problem with the VCS.
        """


class IRemoteBranch(IBranch):
    """
    Abstraction of a version control  branch that does not exist in the local
    file system and is beyond our control.
    """

    @abstractproperty
    def url(self):
        """
        VCS-specific URL of this branch.
        """

    @abstractmethod
    def sprout_to_pathname(self, pathname):
        """
        Create a local branch from the copy of the remote branch an its current
        state.
        
        :return Locally created Branch
        :raises VCSFailure: when there is some other problem with the VCS.
        """


class IVCS(Interface):
    """
    Abstraction of a version control system.

    Has an ability to open a branch from a pathname.
    """

    @abstractmethod
    def open_local(self, pathname):
        """
        Get an instance of ILocalBranch pointing at the specified pathname.

        .. note::
            This method is a workaround for lack of abstractclassmethod. It
            belongs on the ILocalBranch interface really.
        """

    @abstractmethod
    def open_remote(self, url):
        """
        Get an instance of IRemoteBranch pointing at the specified URL
        """
