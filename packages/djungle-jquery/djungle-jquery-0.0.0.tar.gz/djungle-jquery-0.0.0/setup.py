#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Djungle jQuery – jQuery as Django app
# Copyright © 2012  Hendrik M Halkow
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
"""
Installation script for djungle-jquery.
"""

import os
import shutil
import glob
from setuptools import setup, find_packages
from distutils.command.build import build
from subprocess import call



class MakeBuild(build):
    """
    Custom build class that is used to make jQuery via Makefile.
    """
    def run(self):
        """
        Run the build script and call common build script.
        """
        work_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                'modules', 'jquery'))

        static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                'djungle', 'jquery', 'static', 'djungle', 'jquery'))

        target_dir = os.path.join(static_dir, 'jquery')

        if not os.path.isdir(static_dir):
            os.makedirs(static_dir)

        if os.path.isdir(target_dir):
            shutil.rmtree(target_dir)

        os.makedirs(target_dir)

        call(['make',], cwd=work_dir)
        
        shutil.copy(os.path.join(work_dir, 'dist', 'jquery.min.js'),
            os.path.join(target_dir, 'jquery.js'))

        build.run(self)


def main():
    """
    The main entry point of the setup script.
    """
    readme_file = open(os.path.join(os.path.dirname(__file__), 'README.md'))
    readme = readme_file.read()
    readme_file.close()

    setup(
        name='djungle-jquery',
        version='0.0.0',
        description='jQuery as Django app',
        long_description=readme,
        author='Hendrik M Halkow',
        author_email='hendrik@halkow.com',
        url='https://github.com/djungle/djungle-jquery',
        classifiers=[
            'Development Status :: 1 - Planning',
            'Environment :: Web Environment',
            'Framework :: Django',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: GNU General Public License (GPL)',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Internet :: WWW/HTTP',
            'Topic :: Software Development :: User Interfaces',
            'Topic :: Text Processing :: Markup :: HTML'
        ],
        install_requires=[
            'Django>=1.3.1',
        ],
        packages=find_packages(),
        package_data={
            'djungle.jquery': [
                'static/djungle/jquery/*',
            ],
        },
        namespace_packages=['djungle'],
        zip_safe=False,
    )


if __name__ == '__main__':
    main()
