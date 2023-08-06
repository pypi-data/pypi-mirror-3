#! /usr/bin/env python
# *-* coding:utf-8 *-*
# LingPy 
#
# Copyright (C) 2012 Johann-Mattis List 
# Author: Johann-Mattis List
# Author Email: <mattis.list@phil.uni-duesseldorf.de> URL: <http://lingulist.de/lingpy> For
# license information, see <gpl-3.0.txt>

import distribute_setup
distribute_setup.use_setuptools()

from setuptools import setup, find_packages,Extension

setup(
        name = "lingpy",
        version = "1.0",
        packages = find_packages(),
        include_package_data = True,
        install_requires = ['numpy','networkx'],
        author = "Johann-Mattis List",
        author_email = "mattis.list@gmail.com",
        keywords = [
            "historical linguistics", 
            "sequence alignment",
            "computational linguistics"
            ],
        url = "http://lingulist.de/lingpy/",
        description = "Python library for automatic tasks in historical linguistics",
        license = "gpl-3.0",
        platforms = ["unix","linux"],
        ext_modules=[
            Extension(
                'lingpy.algorithm.align',
                ['lingpy/algorithm/align.pyx'],
                )
            ]
        )


