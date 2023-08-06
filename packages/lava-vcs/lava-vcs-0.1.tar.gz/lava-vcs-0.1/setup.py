#!/usr/bin/env python
#
# Copyright (C) 2010, 2011 Linaro Limited
#
# Author: Zygmunt Krynicki <zygmunt.krynicki@linaro.org>
#
# This file is part of lava-vcs
#
# lava-vcs is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation
#
# lava-vcs is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with lava-vcs.  If not, see <http://www.gnu.org/licenses/>.


try:
    from setuptools import setup, find_packages
except ImportError:
    print "This package requires setuptools to be configured"
    print "It can be installed with debian/ubuntu package python-setuptools"
    raise


setup(
    name='lava-vcs',
    version=":versiontools:lava.vcs:",
    author="Zygmunt Krynicki",
    author_email="zygmunt.krynicki@linaro.org",
    namespace_packages=['lava'],
    packages=find_packages(),
    license="AGPL",
    entry_points="""
    [lava.vcs.adapters]
    bzr = lava.vcs.adapters.bzr:Bzr
    git = lava.vcs.adapters.git:Git
    [lava_server.extensions]
    vcs = lava.vcs.extension:VCSExtension
    """,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Testing"],
    install_requires=[
        'lava-server >= 0.7',
        'lava-celery >= 0.1.1',
        'versiontools >= 1.8',
    ],
    setup_requires=[
        'versiontools >= 1.8'
    ],
    zip_safe=False,
    include_package_data=True
)
