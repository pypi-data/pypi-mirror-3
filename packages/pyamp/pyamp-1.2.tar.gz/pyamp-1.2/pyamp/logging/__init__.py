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
'''The logging module contains a series of modules which aim to improve
the ease of debugging a system through logging messages to a given stream.

The :class:`pyamp.logging.logger.Logger` class is the central class to the
logging module. It is essentially a wrapper class for the Python :mod:`logging`
module and provides extended functionality such as: adding prefixes to the
logged messages, and logging colored messages to the console.

'''
from meta import *
from colors import *
from logger import *
from prefix import *
from loggable import *
