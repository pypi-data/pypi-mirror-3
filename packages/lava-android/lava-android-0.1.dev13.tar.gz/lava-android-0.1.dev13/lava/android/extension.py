# Copyright (C) 2010, 2011 Linaro Limited
#
# Author: Zygmunt Krynicki <zygmunt.krynicki@linaro.org>
#
# This file is part of LAVA Android.
#
# LAVA Android is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License version 3
# as published by the Free Software Foundation
#
# LAVA Android is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with LAVA Android.  If not, see <http://www.gnu.org/licenses/>.

from lava_server.extension import ILavaServerExtension

import versiontools
import lava.android 


class AndroidExtension(ILavaServerExtension):

    def __init__(self, slug):
        self.slug = slug

    def contribute_to_settings(self, settings_module):
        settings_module['INSTALLED_APPS'].append('lava.android')

    def contribute_to_settings_ex(self, settings_module, settings_obj):
        pass

    def contribute_to_urlpatterns(self, urlpatterns, mount_point):
        pass

    @property
    def api_class(self):
        return None

    @property
    def name(self):
        return "Android"

    @property
    def version(self):
        return versiontools.format_version(lava.android.__version__, lava.android)

    @property
    def front_page_template(self):
        return None

    def get_front_page_context(self):
        return {}

    def get_main_url(self):
        pass

    def get_menu(self):
        pass
