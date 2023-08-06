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

from lava_projects.models import Project
from django_restricted_resource.models import RestrictedResource


# class Repository(RestrictedResource):
#
#    url = models.CharField(max_length=1000)
#
#    project = models.ForeignKey(
#        Project,
#        related_name='repositories')
#
#    adapter = models.CharField(
#        max_length=32,
#        choices=(
#            ('bzr', "Bazaar"),
#            ('git', "Git"),
#        ))

