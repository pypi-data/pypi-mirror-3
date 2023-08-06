# Copyright (C) 2012 Linaro Limited
#
# Author: Andy Doan <andy.doan@linaro.org>
#
# This file is part of LAVA Android Benchmark Views. It was based
# on code from LAVA Kernel CI Views
#
# LAVA Android Benchmark Views is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License version 3
# as published by the Free Software Foundation
#
# LAVA Android Benchmark Views is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with LAVA Android Benchmark Views.  If not, see <http://www.gnu.org/licenses/>.

import versiontools
from lava_server.extension import LavaServerExtension

import android_benchmark_views_app


class AndroidBenchmarkViewsExtension(LavaServerExtension):
    """
    Lava Android Benchmark extension.
    """

    @property
    def app_name(self):
        return "android_benchmark_views_app"

    @property
    def name(self):
        return "Android Benchmarks"

    @property
    def main_view_name(self):
        return "android_benchmark_views_app.views.index"

    @property
    def description(self):
        return "Android Benchmark Views application for LAVA server"

    @property
    def version(self):
        return versiontools.format_version(android_benchmark_views_app.__version__, hint=android_benchmark_views_app)
