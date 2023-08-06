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
'''The rstGeneration module contains classes and functions which provide
the ability to generate a single reStructured text formatted file for
each of the modules contained within a main Python project.

'''
from os import curdir
from datetime import date
from optparse import OptionParser
from os.path import abspath, basename, exists, join, split, splitext

from pyamp.logging import Loggable
from pyamp.util import getPythonContents, getClasses


class RstOptions:
    '''The RstOptions class encapsulates all the options that can be passed
    to the RST generation class to configure the generated output.

    '''
    def __init__(self, inheritance=True, overwrite=False, extension='.rst',
                 ignoredModules=None, modifiedDirectory="_modified"):
        '''
        * inheritance -- True to include inheritance diagrams for each class
        * overwrite -- True to overwrite existing files
        * extension -- The extension to use for generated files
        * ingoreModules -- The list of modules to ignore (i.e., no RST files
                           will be created for these modules)
        * modifiedDirectory -- The modified directory

        '''
        self.inheritance = inheritance
        self.overwrite = overwrite
        self.extension = extension
        self.ignoredModules = [] if ignoredModules is None else ignoredModules
        self.modifiedDirectory = modifiedDirectory


class RstBase(Loggable):
    '''The RstBase class provides the base functionality used to create
    RstFiles based off of Python modules. It takes a module name and
    provides the ability to write the output in reStructured text format.

    '''

    contentFunctions = []
    '''The contentFunctions property should be set to a list of class
    function names. These functions will be called, in order, to return a list
    of lines to add to the final generated file.

    Each content function takes an :class:`RstOptions` object as its only
    parameter, and should return a list of strings.

    '''

    def __init__(self, moduleName, logData=None):
        '''
        * moduleName -- The name of the module which contains this module
        * logData -- The LogData object

        '''
        Loggable.__init__(self, self.__class__.__name__, logData)

        self._moduleName = moduleName
        self._currentModuleName = '.'.join(moduleName.split('.')[0:-1])
        self._projectName = moduleName.split('.')[0]
        self._baseName = moduleName.split('.')[-1]

    def write(self, directory, options):
        '''Generate the reStructured text formatted file for this
        Python module.

        * directory -- The output directory in which to write the file
        * options -- The RstOptions to use when generating the file

        '''
        filename = join(directory, self._getFilename(options))

        # Only create the RST file if: the file does not exist, or we are
        # allowed to overwrite existing files, and this module is not expected
        # to be ignored
        if (not exists(filename) or options.overwrite) and \
                self._baseName not in options.ignoredModules:
            content = self._toRst(options)

            if exists(filename):
                self.warn("Overwriting existing file [%s]" % self._baseName)

            # Write the file contents
            fd = file(filename, 'w')
            fd.write(content)
            fd.close()
        else:
            filename = None

        return filename

    def _getFilename(self, _options):
        '''Return the name of the RST file to write.

        .. note:: This function **must** be overridden by subclasses.

        * _options -- The :class:`RstOptions` object

        '''
        # @todo: use an error class
        raise Exception("This function must be implemented by subclasses!")

    def _toRst(self, options):
        '''Convert the Python module to a reStructured text file.

        .. warning:: This function will raise an :class:`AttributError` in the
           event that the class does not contain one of the function names
           listed in the :attr:`contentFunctions` property.

        * options -- The RstOptions to use

        '''
        lines = []

        # Create lines for all the different parts of content needed to
        # create this RST file
        for name in self.contentFunctions:
            # Attempt to locate the function
            # Note: This will throw an AttributeError if the function name
            # could not be found
            function = getattr(self, name)

            lines.extend(function(options))

            # Add an empty line to all but the last function
            if function != self.contentFunctions[-1]:
                lines.append("")

        return '\n'.join(lines)


class RstModuleDirectory(RstBase):
    '''The RstModuleDirectory encapsulates the functionality of writing a
    file in reStructured text format for a given Python module which is
    a directory containing one or more Python sub-modules.

    '''
    ModulePrefix = "mod_"

    contentFunctions = [
        "_getTitle",
        "_getTocTree",
        "_getSubModules"
        ]

    def __init__(self, moduleName, subFiles, subDirectories, logData=None):
        '''
        * moduleName -- The name of the module which contains this module
        * subFiles -- The list of sub-file modules for this module
        * subDirectories -- The list of sub-directory module for this module
        *  -- The LogData object

        '''
        RstBase.__init__(self, moduleName, logData)
        self.__files = subFiles
        self.__directories = subDirectories

    def _getFilename(self, options):
        '''Return the name of the RST file to write.

        * options -- The :class:`RstOptions` object

        '''
        # Replace periods with underscores in the module name for
        # use in the filename
        moduleName = self._moduleName.replace(".", "_")

        # Prefix the filename to indicate that this is a module directory entry
        return "%s%s%s" % (self.ModulePrefix, moduleName, options.extension)

    def _getTitle(self, _options):
        '''Return reStructured text lines needed to create the title for this
        Python module

        * options -- The :class:`RstOptions` object

        '''
        title = "The %s module" % self._baseName
        titleLine = "=" * 80

        return [titleLine, title, titleLine]

    def _getTocTree(self, _options):
        '''Return the reStructured text lines needed to create the table of
        contents tree for this Python module.

        * options -- The :class:`RstOptions` object

        '''
        lines = [
            ".. toctree::",
            "   :maxdepth: 3"
            ]

        return lines

    def _getSubModules(self, options):
        '''Return the reStructured text lines needed to create the list of
        sub-modules for this Python module.

        * options -- The :class:`RstOptions` object

        '''
        dirs = [self.__getDir(name, options) for name in self.__directories]
        files = [self.__getFile(name, options) for name in self.__files]

        # Place the directory entries before the file entries
        return dirs + files

    def __getFile(self, moduleName, options):
        '''Return the reStructured text lines needed to create a single table
        of contents entry for this Python module corresponding to a single
        Python file.

        * options -- The :class:`RstOptions` object

        '''
        spacing = " " * 3

        # Grab the base module name for this file
        baseName = moduleName.split(".")[-1]

        # Replace periods with underscores to correlate to the actual RST
        # file name
        moduleName = moduleName.replace(".", "_")

        # Add the modified directory location if this module is found
        # in the list of modules to ignore
        ignoredModules = options.ignoredModules
        if baseName in ignoredModules or moduleName in ignoredModules:
            moduleName = "../%s/%s" % (options.modifiedDirectory, moduleName)

        # Add spacing to the front of the module name, 
        return "%s%s" % (spacing, moduleName)

    def __getDir(self, moduleName, options):
        '''Return the reStructured text lines needed to create a single table
        of contents entry for this Python module corresponding to a directory
        containing one or more Python file.

        * options -- The :class:`RstOptions` object

        '''
        spacing = " " * 3

        # Grab the base module name for this file
        baseName = moduleName.split(".")[-1]

        # Replace periods with underscores to correlate to the actual RST
        # module name
        moduleName = moduleName.replace(".", "_")

        # Add the modified directory location if this module is found
        # in the list of modules to ignore
        ignoredModules = options.ignoredModules
        if baseName in ignoredModules or moduleName in ignoredModules:
            moduleName = "../%s/%s" % (options.modifiedDirectory, moduleName)

        # Add spacing to the front of the module name, and replace periods with
        # underscores to correlate to the actual RST file name
        return "%s%s%s" % (spacing, self.ModulePrefix, moduleName)


class RstModule(RstBase):
    '''The RstModule class encapsulates the functionality of writing a
    file in reStructured text format for a given Python module which is
    a single Python file.

    '''
    contentFunctions = [
        "_getComment",
        "_getTitle",
        "_getAutoModule",
        "_getAutoClasses",
        ]

    def __init__(self, moduleName, logData=None):
        '''
        * moduleName -- The name of the module which contains this module
        * logData -- The LogData object

        '''
        RstBase.__init__(self, moduleName, logData)

        # Find all of the classes contained within this module
        self.__classes = self.__findClasses()

    def _getFilename(self, options):
        '''Return the name of the RST file to write.

        * options -- The :class:`RstOptions` object

        '''
        # Convert periods to underscores in the module name for
        # use in the filename
        moduleName = self._moduleName.replace(".", "_")

        # Create a filename with the module name as a prefix
        return "%s%s" % (moduleName, options.extension)

    def _getComment(self, _options):
        '''Get the reStructured text lines for the auto generated comment.

        * _options -- The RstOptions to use

        '''
        timestamp = date.today().strftime("%B %d, %Y")

        lines = [
            ".. %s documentation file, created by" % self._projectName,
            "   generateRsts for %s on %s" % (self._moduleName, timestamp),
            "   This file should not be modified."
            ]

        return lines

    def _getTitle(self, _options):
        '''Get the reStructured text lines for the title for this module.

        * _options -- The RstOptions to use

        '''
        title = "The %s module" % self._baseName
        titleLine = "=" * (len(title) + 1)

        return [titleLine, title, titleLine]

    def _getAutoModule(self, _options):
        '''Get the reStructured text lines for the automodule directive.

        * _options -- The RstOptions to use

        '''
        return [".. automodule:: %s" % self._moduleName]

    def _getAutoClasses(self, options):
        '''Get the reStructured text lines for all the autoclass directives
        for this module.

        * options -- The RstOptions to use

        '''
        lines = []

        index = 1
        for className in self.__classes:
            lines.extend(self.__getAutoClass(className, options))

            # Add an empty line to all but the last class
            if index < len(self.__classes):
                lines.append("")
            index += 1

        return lines

    def __getAutoClass(self, className, options):
        '''Get the reStructured text lines for a single autoclass directive.
        
        * className -- The name of the class
        * options -- The RstOptions to use

        '''
        # Get the full module name of the class
        fullClassName = '.'.join([self._moduleName, className])

        title = "The %s class" % className
        titleLine = "-" * (len(title) + 1)

        # Add the title to the lines
        lines = [titleLine, title, titleLine, ""]

        # Create the line to add the inheritance diagram
        if options.inheritance:
            inheritance = ".. inheritance-diagram:: %s" % fullClassName
            lines.extend([inheritance, ""])

        # Create the lines to include the class and its members
        autoClass = ".. autoclass:: %s" % fullClassName
        members = "    :members:"

        # Add the auto class directive
        lines.extend([autoClass, members])

        return lines

    def __findClasses(self):
        '''Find the list of classes for this Python module'''
        try:
            classes = getClasses(self._moduleName)
        except Exception, e:
            self.error("Failed to locate classes for [%s]" % self._moduleName)
            classes = {}

        # Only keep classes that are actually part of the current project
        classes = [t[0] for t in classes.items() if self.__isProjectClass(t)]

        return classes

    def __isProjectClass(self, classTuple):
        '''Determine if the given class tuple (where the first element in the
        tuple is the class name and the second element in the tuple is the
        class object) is part of the current module.

        * classTuple -- The class tuple

        '''
        className = str(classTuple[1])
        searchFor = "%s." % self._currentModuleName

        return className.startswith(self._currentModuleName) or \
            searchFor in str(classTuple[1])


def locateRsts(moduleName, directory):
    '''Return the list of :class:`RstModule`s contained within the given
    directory for the given project module name.

    * moduleName -- The module name for the Python project
    * directory -- The directory containing the Python modules

    '''
    rsts = []

    # Grab the contents of the current directory
    files, subDirectories = getPythonContents(directory, absPath=True)

    # Determine if this is a proper Python module
    initFile = "__init__.py"
    fileBases = dict([(basename(f), f) for f in files])

    # Only continue for valid Python module directories (i.e., those containing
    # the __init__.py file)
    if initFile in fileBases:
        # Remove the init file from the list of files because we do not want
        # to generate an RST file for this file
        files.remove(fileBases[initFile])
        
        # Keep track of the list of sub-modules (files and directories)
        # for the current module
        subModuleFiles = []
        subModuleDirs = []

        # Generate RST classes for all of the files in this directory
        for filename in files:
            baseName = splitext(basename(filename))[0]

            # Ignore any files starting with an underscore
            if not baseName.startswith("_"):
                fullModuleName = '.'.join([moduleName, baseName])

                # Only process the module once
                if fullModuleName not in subModuleFiles:
                    rsts.append(RstModule(fullModuleName))

                    # This file is a sub-module
                    subModuleFiles.append(fullModuleName)

        # Generate RST classes for all of the sub directories
        for subDirectory in subDirectories:
            newModuleName = '.'.join([moduleName, basename(subDirectory)])

            # Recurse to find the RST files for this sub-directory
            subRsts = locateRsts(newModuleName, subDirectory)

            # If the directory contained modules then we should keep
            # track of it
            if len(subRsts) > 0 and newModuleName not in subModuleDirs:
                rsts.extend(subRsts)
                
                # This directory is a sub-module
                subModuleDirs.append(newModuleName)

        # Add an entry for the module directory
        rsts.append(RstModuleDirectory(moduleName, subModuleFiles,
                                       subModuleDirs))

    return rsts


def writeRsts(rsts, outputDirectory, options):
    '''Generate a single reStructured text file for all of the given
    :class:`.RstModule` objects. These files will be generated in the
    output directory. Use the given RstOptions when generating the files.

    * rsts -- The list of :class:`.RstModule` objects
    * outputDirectory -- The output directory where the files will be saved
    * options -- The RstOptions to use

    '''
    generated = []

    if exists(outputDirectory):
        # Write all of the RST files to the output directory
        for rst in rsts:
            generated.append(rst.write(outputDirectory, options))
            
    else:
        # @todo: use amp error
        raise Exception("Output directory [%s] does not exist!" % \
                            outputDirectory)

    # Return the list of files that were generated (filter out None which
    # indicates that a file was not created)
    return [filename for filename in generated if filename is not None]


def generateAllRsts(projectName, ignoredModules):
    '''Locate and generate reStructured text files for all of the Python
    modules located within the given project name and also being sure to ignore
    any modules that are in the list of modules to ignore.

    .. note:: This assumes a standard doctools Python project setup structure
       and that this function will be called from a script located within the
       'doc' directory.

    '''
    parser = OptionParser()

    # Create command line options which provide the ability to configure the
    # RST creation from the command line
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true",
                      default=False, help="True for verbose mode.")
    parser.add_option("-f", "--force", dest="force", action="store_true",
                      default=False, help="Overwrite existing files.")
    parser.add_option("--noInheritance", dest="noInheritance", default=False,
                      action="store_true",
                      help="Do not include inheritance graphs for " \
                          "all of the classes.")
    parser.add_option("--extension", dest="extension", default='.rst',
                      help="The extension used to save the RST files " \
                          "default is '.rst'.")
    parser.add_option("-d", "--dest", dest="destination",
                      default='source/_generated',
                      help="The destination directory for the generated RST " \
                          "files. Default is source/_generated.")
    parser.add_option("--modified", dest="modifiedDirectory",
                      default='_modified',
                      help="The name of the directory where modified RST " \
                          "files pertaining to modules within this project " \
                          "are stored. Default is source/_modified. Note: " \
                          "The modified directory must be at the same level " \
                          "as the generated directory!")

    (options, _) = parser.parse_args()

    # Pop up one directory to get the project trunk directory, and then
    # underneath that should be a directory with the same name as the project
    # which should contain all of the source files
    cwd = abspath(curdir)
    projectTrunkDir = split(cwd)[0]
    projectSourceDir = join(projectTrunkDir, projectName)

    # Create the RST options
    rstOptions = RstOptions(inheritance=not options.noInheritance,
                            overwrite=options.force,
                            extension=options.extension,
                            ignoredModules=ignoredModules,
                            modifiedDirectory=options.modifiedDirectory)

    # Locate all of the RST files for the project
    rsts = locateRsts(projectName, projectSourceDir)

    # Generate all of the reStructured text files for this project
    generated = writeRsts(rsts, options.destination, rstOptions)

    # Display output to the user
    print "Generated [%d] files..." % len(generated)

    # Print out all of the generated files for verbose mode
    if options.verbose:
        for gen in generated:
            print "    ", gen

    return generated
