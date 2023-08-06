#!/usr/bin/env python
#
# Copyright (C) 2011 Linaro Limited
#
# Author: Alexandros Frantzis <alexandros.frantzis@linaro.org>
#
# This file is part of LAVA Server.
#
# LAVA Server is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation
#
# LAVA Server is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with LAVA Server.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages


setup(
    name='linaro-graphics-dashboard',
    version=":versiontools:linaro_graphics_app:",
    author="Alexandros Frantzis",
    author_email="alexandros.frantzis@linaro.org",
    packages=find_packages(),
    license="AGPL",
    description="Linaro Graphics WG application for LAVA Server",
    entry_points="""
    [lava_server.extensions]
    graphics = linaro_graphics_app.extension:LinaroGraphicsExtension
    """,
    long_description="""
    """,
    install_requires=["lava-server >= 0.2"],
    setup_requires=["versiontools >= 1.4"],
    zip_safe=False,
    include_package_data=True)
