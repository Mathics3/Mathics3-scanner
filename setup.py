#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Setuptools based setup script for Mathics.

For the easiest installation just type the following command (you'll probably
need root privileges):

    python setup.py install

This will install the library in the default location. For instructions on
how to customize the install procedure read the output of:

    python setup.py --help install

In addition, there are some other commands:

    python setup.py clean -> will clean all trash (*.pyc and stuff)

To get a full list of available commands, read the output of:

    python setup.py --help-commands

Or, if all else fails, feel free to write to the mathics users list at
mathics-users@googlegroups.com and ask for help.
"""

import os
import os.path as osp

from setuptools import setup
from setuptools.command.build_py import build_py as setuptools_build_py


def get_srcdir():
    """Return the directory of the location if this code"""
    filename = osp.normcase(osp.dirname(osp.abspath(__file__)))
    return osp.realpath(filename)


class build_py(setuptools_build_py):
    def run(self):
        for table_type in ("boxing-character", "named-character", "operator"):
            json_data_file = osp.join("data", f"{table_type}.json")
            json_path = osp.join("mathics-scanner", json_data_file)
            if not osp.exists(json_path):
                os.system(f"mathics3-make-{table_type}-json -o {json_path}")
            self.distribution.package_data["Mathics-Scanner"].append(json_data_file)
        setuptools_build_py.run(self)


CMDCLASS = {"build_py": build_py}


setup(
    cmdclass=CMDCLASS,
    # don't pack Mathics3 an in egg because of media files, etc.
    zip_safe=False,
)
