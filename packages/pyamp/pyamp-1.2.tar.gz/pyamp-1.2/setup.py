#!/usr/bin/python
# Copyright 2012 Brett Ponsler
# This file is part of pyamp.
#
# pyamp is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyamp is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyamp.  If not, see <http://www.gnu.org/licenses/>.
from setuptools import setup


setup(name='pyamp',
      version='1.2',
      description='pyamp module for Python',
      author='Brett Ponsler',
      author_email='ponsler@gmail.com',
      url='https://code.google.com/p/pyamp/',
      packages=['pyamp', 'pyamp.config', 'pyamp.logging', 'pyamp.networking',
                'pyamp.networking.sockets', 'pyamp.patterns',
                'pyamp.patterns.interfaces', 'pyamp.processes',
                'pyamp.processes.threading', 'pyamp.system',
                'pyamp.system.ubuntu', 'pyamp.ui', 'pyamp.ui.input',
                'pyamp.ui.qt', 'pyamp.util', 'pyamp.web',
                'pyamp.web.http', 'pyamp.web.html', 'pyamp.documentation'],
      data_files=[('pyamp/files', ['files/admin.txt'])],
      license='GNU GPL v3',
      )
