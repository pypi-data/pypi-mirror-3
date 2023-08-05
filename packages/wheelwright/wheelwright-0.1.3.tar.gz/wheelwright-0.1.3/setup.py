#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import wheelwright

long_description = open("README.txt").read()

setup(name="wheelwright",
      version=wheelwright.__version__,
      url="http://biciworks.com/wheelwright/",
      license="GPLv3",
      author="Kris Andersen",
      author_email="kris@biciworks.com",
      description="Bicycle wheel tension visualizer",
      long_description=long_description,
      zip_safe=False,
      classifiers=[
            "Development Status :: 3 - Alpha",
            "Environment :: MacOS X",
            "Environment :: X11 Applications",
            "Environment :: Win32 (MS Windows)",
            "Intended Audience :: End Users/Desktop",
            "Intended Audience :: Science/Research",
            "Natural Language :: English",
            "License :: OSI Approved :: GNU General Public License (GPL)",
            "Operating System :: OS Independent",
            "Programming Language :: Python",
            "Topic :: Education",
            "Topic :: Scientific/Engineering",
            ],
      platforms="any",
      packages=find_packages(exclude=["tests"]),
      include_package_data=True,
      setup_requires=["nose", "py2app"],
      test_suite="nose.collector",
      install_requires=["numpy", "matplotlib", "rst2pdf", "pil"],
      entry_points={"gui_scripts": ["wheelwright = wheelwright:main"]},
      app=["wheelwright/wheelwright.py"]
      )
