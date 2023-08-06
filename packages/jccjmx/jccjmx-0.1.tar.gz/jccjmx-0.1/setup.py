#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
#=============================================================================
# Copyright   : (c) 2012 semantics GmbH. All Rights Reserved.
# Rep./File   : $URL: https://svn.semantics.de/1%20Produkte/VisualLibrary/trunk/software/misc/jccjmx/setup.py $
# Date        : $Date: 2012-05-07 16:08:45 +0200 (Mo, 07. Mai 2012) $
# Author      : Christian Heimes
# Worker      : $Author: c.heimes $
# Revision    : $Rev: 40353 $
# Purpose     : distutils setup routines
#=============================================================================
from distutils.core import setup

setup_info = dict(
    name="jccjmx",
    version="0.1",
    description="Java Management Extension (JMX) wrapper for JCC",
    long_description=open("README.txt").read(),
    setup_requires=["JCC>=0.12", "PyLucene=>3.4"],
    author="semantics GmbH / Christian Heimes",
    author_email="c.heimes@semantics.de",
    maintainer="Christian Heimes",
    maintainer_email="c.heimes@semantics.de",
    url="http://www.semantics.de",
    keywords="java jcc jmx rmi ",
    license="Sun Public License",
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Sun Public License',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Java',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Software Development :: Debuggers'
    ),
)

setup(**setup_info)
