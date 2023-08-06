#!/usr/bin/env python
#
# Copyright (C) 2012 Linaro Limited
#
# Author: Zygmunt Krynicki <zygmunt.krynicki@linaro.org>
#
# This file is part of LAVA Fast Models
#
# LAVA Fast Models is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License version 3
# as published by the Free Software Foundation
#
# LAVA Fast Models is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with LAVA Fast Models.  If not, see <http://www.gnu.org/licenses/>.


try:
    from setuptools import setup, find_packages
except ImportError:
    print "This package requires setuptools to be configured"
    print "It can be installed with debian/ubuntu package python-setuptools"
    raise


setup(
    name='lava-fastmodels',
    version=":versiontools:lava.fastmodels:",
    author="Zygmunt Krynicki",
    author_email="zygmunt.krynicki@linaro.org",
    test_suite="unittest2.collector",
    namespace_packages=['lava'],
    packages=find_packages(),
    description="ARM Fast Models support code for LAVA",
    long_description=open('README').read(),
    license="AGPL",
    entry_points="""
    [lava.commands]
    nfs = lava.nfs.commands:NFSCommand
    fastmodel = lava.fastmodels.commands:FastModelCommand
    [lava.nfs.commands]
    export = lava.nfs.commands:ExportCommand
    unexport = lava.nfs.commands:UnExportCommand
    [lava.fastmodels.commands]
    build = lava.fastmodels.commands:BuildCommand
    list = lava.fastmodels.commands:ListCommand
    """,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Testing"],
    install_requires=[
        'json-document',
        'lava-tool >= 0.3a1',
        'versiontools >= 1.8.2',
        'lava-utils-interface >= 1.0',
    ],
    setup_requires=[
        'versiontools >= 1.8.2',
    ],
    tests_require=[
        'unittest2',
    ],
    zip_safe=True,
    include_package_data=True
)
