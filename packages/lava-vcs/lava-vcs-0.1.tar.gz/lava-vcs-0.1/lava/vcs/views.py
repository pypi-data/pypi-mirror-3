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

from django.http import HttpResponse
from django.template import RequestContext, loader
from django.utils.translation import ugettext as _

from lava_server.views import index as lava_index
from lava_server.bread_crumbs import (
    BreadCrumb,
    BreadCrumbTrail,
)


@BreadCrumb(_("VCS"), parent=lava_index)
def index(request):
    template_name = "lava/vcs/index.html"
    t = loader.get_template(template_name)
    c = RequestContext(request, {
        'bread_crumb_trail': BreadCrumbTrail.leading_to(index)})
    return HttpResponse(t.render(c))
