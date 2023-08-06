"""
Unzip python helper. 
    Extracts a zip file to the filesystem.
        
Copyright (C) 2006 Simon Eisenmann, 

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

Author: Simon Eisenmann
Contact: longsleep@gmail.com
"""

# Imports.
import os
import sys
import zipfile

from distutils.dir_util import mkpath


class Unzip:
    """
    Extract zip files to the filesystem.
    """
    
    def extract(self, file, destination):
        """
        Extracts zip file to destination folder.
        """
        
        if isinstance(file, basestring):
            file = os.path.abspath(os.path.expanduser(os.path.normpath(file)))
        
        # Create zip instance.
        zip = zipfile.ZipFile(file)
        
        # Normalize path.
        destination = os.path.abspath(os.path.expanduser(os.path.normpath(destination)))
        
        # First create folder structure.
        self._folders(zip, destination)
        
        # Create files.
        self._files(zip, destination)
        
        # Cleanup.
        zip.close()


    def _folders(self, zip, destination):
        """
        Creates the folder structure.
        """
        
        folders = {}
        
        for f in zip.namelist():
            f = os.path.dirname(f)
            folders[f]=True
                
        # Sort so that we can simply mkdir through the list.
        folders = folders.keys()
        folders.sort()
    
        # Create all folders.
        for f in folders:
            f = os.path.join(destination, f)
            if not os.path.exists(f):
                mkpath(f)


    def _files(self, zip, destination):
        """
        Extracts all files into the folder structure.
        """
        
        for f in zip.namelist():
            if not f.endswith('/'):
                fp = file(os.path.join(destination, f), 'wb')
                fp.write(zip.read(f))
                fp.flush()
                fp.close()
    

def unzip(file, destination):
    """
    Main function.
    """
    worker = Unzip()
    worker.extract(file, destination)
    return True
    

if __name__ == '__main__':
    """
    Commandline mode.
    """
    
    args = sys.argv[1:]
        
    if len(args) != 2:
        
        print >>sys.stderr, "Usage: unzip.py ZIPFILE DESTINATIONPATH"
        sys.exit(1)
        
    # Extract.
    unzip(*args)
    
    
