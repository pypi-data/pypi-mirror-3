#!/usr/bin/env python
#
# Copyright (C) 2012 Linaro Limited
#
# Author: Zygmunt Krynicki <zygmunt.krynicki@linaro.org>
#
# This file is part of LAVA Raven.
#
# LAVA Raven is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation
#
# LAVA Raven is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with LAVA Raven.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages


setup(
    name='lava-raven',
    version=":versiontools:lava.raven:",
    author="Zygmunt Krynicki",
    author_email="zygmunt.krynicki@linaro.org",
    namespace_packages=['lava'],
    packages=find_packages(),
    entry_points="""
        [lava_server.extensions]
        raven=lava.raven.extension:RavenExtension
    """,
    license="LGPL",
    description="Raven/Sentry support for LAVA Server",
    long_description=open("README.rst").read(),
    url='https://launchpad.net/lava-raven',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        ("License :: OSI Approved :: GNU Library or Lesser General Public"
         " License (LGPL)"),
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Testing",
    ],
    install_requires=[
        'lava-server >= 0.9.1',
        'raven >= 1.4.2',
        'versiontools >= 1.8',
    ],
    setup_requires=[
        'versiontools >= 1.8',
    ],
    zip_safe=True)
