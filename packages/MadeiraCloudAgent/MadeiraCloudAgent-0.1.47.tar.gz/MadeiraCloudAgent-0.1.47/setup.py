#!/usr/bin/env python
#-*- coding:utf-8 -*-

from setuptools import setup, find_packages

setup(
		name = "MadeiraCloudAgent",
        version="0.1.47",
        packages = ["MadeiraCloudAgent","MadeiraCloudAgent/monitor","MadeiraCloudAgent/psutil","MadeiraCloudAgent/lib","MadeiraCloudAgent/lib64"], 
        package_data = {'': ['*.*']},
        zip_safe = False,		
        description = "Agent For MadeiraCloud",
        long_description = "Agent For MadeiraCloud AWS",
        author = "MadeiraCloud",
        author_email = "support@madeiracloud.com",

		#scripts=['scripts/MadeiraCloudAgent'],
        license = "GPL",
        keywords = ("MadeiraCloud", "egg"),
        #platforms = "Unix",
        url = "www.madeiracloud.com",
        )
