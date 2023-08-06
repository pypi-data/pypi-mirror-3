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

import logging
import os
import subprocess

from lava.vcs.errors import VCSFailure


class CommonBranchMixIn(object):
    """
    Common helper that simplifies shell-out commands
    """

    def __init__(self, location):
        self._location = location

    def __repr__(self):
        return "<%s location=%r>" % (
            self.__class__.__name__, self.location)

    @property
    def location(self):
        return self._location

    @property
    def tool_name(self):
        return self.vcs_name

    def _run_tool_cmd(self, args, out_of_tree=False, cannot_fail=True):
        kwargs = {}
        # Set the target directory to our location if we are local
        if not self.is_remote and not out_of_tree:
            # Rant: Why cannot bzr have a _consistent_ way of saying "here, do
            # this command against that branch", why cannot "bzr -d $branch"
            # always work
            kwargs['cwd'] = self.location
        # Capture stdout and stderr
        kwargs['stdout'] = subprocess.PIPE
        kwargs['stderr'] = subprocess.PIPE
        # Don't internationalize output.  # Currently bzr does not do it anyway but this may change
        kwargs['env'] = dict(os.environ)
        kwargs['env']['LANG'] = 'C'
        # Construct the command to invoke
        command = [self.tool_name] + args
        kwargs['args'] = command
        # Log what we're doing
        if 'cwd' in kwargs:
            logging.debug("Invoking: %r in %r", command, self.location)
        else:
            logging.debug("Invoking: %r", command)
        # Start the command and let if execute
        proc = subprocess.Popen(**kwargs)
        stdout, stderr = proc.communicate()
        logging.debug("Command finished with code: %d", proc.returncode)
        for line in stdout.splitlines():
            logging.debug("stdout: %s", line)
        for line in stderr.splitlines():
            logging.debug("stderr: %s", line)
        # This is used by the _raise_vcs_fault helper below
        proc.command = command 
        # Overwrite stdout and stderr for easier usage
        proc.stdout, proc.stderr = stdout, stderr
        if proc.returncode != 0 and cannot_fail:
            self._raise_vcs_fault(proc)
        return proc

    def _raise_vcs_fault(self, proc):
        raise VCSFailure(
            "command {command} failed with return code {code}".format(
                command=proc.command, code=proc.returncode))
