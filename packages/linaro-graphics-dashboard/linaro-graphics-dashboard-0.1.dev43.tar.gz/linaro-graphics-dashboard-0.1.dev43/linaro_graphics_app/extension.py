# Copyright (C) 2011 Linaro Limited
#
# Author: Alexandros Frantzis <alexandros.frantzis@linaro.org>
#
# This file is part of LAVA Server.
#
# LAVA Server is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License version 3
# as published by the Free Software Foundation
#
# LAVA Server is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with LAVA Server.  If not, see <http://www.gnu.org/licenses/>.

import versiontools
from lava_server.extension import LavaServerExtension

import linaro_graphics_app


class LinaroGraphicsExtension(LavaServerExtension):
    """
	Linaro Graphics Extension
    """

    @property
    def app_name(self):
        return "linaro_graphics_app"

    @property
    def name(self):
        return "Graphics"

    @property
    def api_class(self):
        from linaro_graphics_app.models import LinaroGraphicsAPI
        return LinaroGraphicsAPI

    @property
    def main_view_name(self):
        return "linaro_graphics_app.views.index"

    @property
    def description(self):
        return "Linaro Graphics extension"

    @property
    def version(self):
        return versiontools.format_version(linaro_graphics_app.__version__)
