#!/usr/bin/env python

import distutils.core
import distutils.cmd
import subprocess

class make_docs(distutils.cmd.Command):
    "build API documentation"

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        subprocess.call(['pydoctor', '--project-name=numm',
            '--resolve-aliases', 'numm/'])

distutils.core.setup(
    name='numm',
    version='0.3',
    url='http://numm.org/numm',
    description='numpy-based multimedia library',
    author='Robert M Ochshorn and Dafydd Harries',
    author_email='rmo@numm.org, daf@numm.org',
    packages=['numm'],
    scripts=['bin/numm-run'],
    classifiers=[
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Environment :: X11 Applications",
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Artistic Software",
        "Topic :: Multimedia",
        "Topic :: Scientific/Engineering",
        ],
    keywords='numerical art numpy gstreamer punk api',
    license='GPL',
    cmdclass={'make_docs': make_docs})
