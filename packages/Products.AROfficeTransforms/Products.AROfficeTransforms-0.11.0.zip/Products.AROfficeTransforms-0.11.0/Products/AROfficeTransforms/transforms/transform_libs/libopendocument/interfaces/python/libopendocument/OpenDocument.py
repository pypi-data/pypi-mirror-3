"""
libopendocument python library for working with OpenDocument 
        files and converting them to XHTML.
        
Copyright (C) 2006 Simon Eisenmann, 
                   Arend van Beelen jr.,
                   Auton Rijnsburg

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

# Imports
import os
import sys
import lxml.etree
import tempfile

from unzip import unzip
from distutils.dir_util import remove_tree
from distutils.file_util import copy_file

# Stylesheet base path
STYLESHEET_PATH = os.path.join(os.path.abspath(os.path.dirname(locals()['__file__'])), 'xsl')


class OpenDocument:
    """
    /**
     * @brief Class with utility functions for working with OpenDocument files.
     *
     * This class allows for opening and closing of OpenDocument files through the
     * use of the open() and close functions(). Documents can also be opened and
     * closed implicitly through the class's constructor and destructor.
     * Modifications to the document can be saved using save().
     *
     * Access to the document's meta-data is provided through the meta() and
     * setMeta() functions.
     *
     * Converting an OpenDocument file to XHTML is possible using the
     * convertToXHTML() function. The setXSLTransformation() and setXSLOption() are
     * there to be able to optimize the result of the conversion for particular
     * purposes.
     *
     * Images in documents may be scaled down using the scaleImages() function.
     *
     * Direct access to the contents of an OpenDocument file is available through
     * the pathToContents() function.
     *
     * @note Implementations may require the availability of the @c zip and @c unzip
     *       utilities.
     */    
    """

    # Namespace definitions.
    dcNS = "http://purl.org/dc/elements/1.1/"
    metaNS = "urn:oasis:names:tc:opendocument:xmlns:meta:1.0"
    officeNS = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"

    filename = None
    
    doc = None
    
    style_doc = None
    style = None
    
    mimetype = None
    
    preprocessor_doc = None
    preprocessor = None
    
    tmp_dir = None
    
    xsl_transformation = None
    xsl_options = None
    

    def __init__(self, filename = ""):
        """
        /**
         * Constructor.
         *
         * Performs initialization operations and opens an OpenDocument
         * file if specified.
         *
         * @param filename Optional path to an OpenDocument file to
         *                 load.
         *
         * @sa open()
         */
        """
        
        self.xsl_transformation = 'default'
        self.xsl_options = {}
            
        # Export files per default.
        self.setXSLOption('export-objects', 'true')
        
        if filename:
            self.open(filename)
         

    def __del__(self):
        """
        /**
         * Destructor.
         *
         * Performs cleanup operations and closes the currently opened
         * document if necessary.
         *
         * @sa close()
         */
        """

        self.close()
        

    def open(self, filename):
        """
        /**
         * Opens the specified OpenDocument for use by the other utility
         * functions in this class.
         *
         * @param filename Path to the OpenDocument file to load.
         *
         * @return @c true if the document was successfully loaded,
         *         @c false otherwise.
         */
        """
        
        if self.filename:
            self.close()
        
        self.filename = filename

        # Create temp directory.
        self.tmp_dir = tempfile.mkdtemp('pylibopendocument')
        
        # Extract zip file.
        unzip(self.filename, self.tmp_dir)
        
        # Open file.
        fp = file(os.path.join(self.tmp_dir, 'content.xml'), 'rb')
        
        # Parse doc.
        self.doc = lxml.etree.parse(fp)
        
        fp.close()
        
        # Read mimetype.
        fp = file(os.path.join(self.tmp_dir, 'mimetype'), 'rb')
        self.mimetype = fp.read().strip()
        fp.close()
        
        return True


    def save(self, filename = ""):
        """
        /**
         * Saves the currently opened document.
         *
         * @param filename Optional filename to save the document to. If
         *                 you omit this parameter, the previously given
         *                 filename is used.
         *
         * @return @c true if the document was successfully saved,
         *         @c false otherwise.
         */
        """
        
        if not filename: filename = self.filename
            
        raise NotImplementedError, "save"


    def close(self):
        """
        /**
         * Closes the currently opened document.
         *
         * Be sure to call save() before closing the document if you
         * have made any modifications to the document you want to save.
         *
         * @sa save()
         */
        """
        
        self.doc = self.mimetype = self.style = self.style_doc = self.filename = None

        # Cleanup temp dir.
        if self.tmp_dir and os.path.isdir(self.tmp_dir):
            remove_tree(self.tmp_dir)

        self.tmp_dir = None
        

    def meta(self, uri, key):
        """
        /**
         * Returns the value of a meta data attribute in the currently
         * opened document.
         *
         * @param uri The namespace URI of the meta data attribute.
         * @param key The node name of the meta data attribute.
         * @return The value of the meta data attribute.
         *
         * @sa setMeta()
         */
        """
        
        raise NotImplementedError, 'meta'


    def setMeta(self, uri, key, value):
        """
        /**
         * Sets the value for a meta data attribute in the currently
         * opened document.
         *
         * If the meta data attribute does not exist yet in the opened
         * document, it will be created.
         *
         * @param uri   The namespace URI of the meta data attribute.
         * @param key   The node name of the meta data attribute.
         * @param value The new value of the meta data attribute.
         * @return @c true if the meta data was set successfully,
         *         @c false otherwise.
         *
         * @sa meta()
         */
        """
        
        raise NotImplementedError, 'setMeta'


    def setXSLTransformation(self, name):
        """
        /**
         * Sets which XSL transformation sheet should be used for
         * converting the document to XHTML.
         *
         * By default, the XSL transformation sheet is set to 'default'.
         *
         * @param name Name of the transformation sheet to use.
         *
         * @sa convertToXHTML()
         */
        """
        
        self.xsl_transformation = name
        
        self.style_doc = None
        self.style = None
        
        # Compute stylesheet file.
        stylesheet = os.path.join(STYLESHEET_PATH, name, 'document2xhtml.xsl')
        
        # Check its there.
        assert os.path.isfile(stylesheet), '%s not found or not a file.' % stylesheet
        
        fp = file(stylesheet, 'rb')
        self.style_doc = lxml.etree.parse(fp)
        fp.close()
        self.style = lxml.etree.XSLT(self.style_doc)


    def setXSLOption(self, key, value):
        """
        /**
         * Sets an XSL option.
         *
         * XSL options are options which are passed to the XSL
         * transformation and which influence how the output from the
         * transformation will look like.
         *
         * Which options are available may differ for the transformation
         * sheet you are using. One option is always available, as it's
         * only partially controlled by the XSL sheet. This is the
         * following option:
         *
         * "export-objects"
         *
         * Possible values: "true" (default), "false".
         * Description: By default, all objects (images, OLE object
         *              replacements) contained within the OpenDocument
         *              file will be exported, together with the
         *              directory they reside in, to the same directory
         *              as the resulting XHTML file upon conversion. By
         *              setting this option to "false", no objects are
         *              exported.
         *
         * @param key   The name of the option to set.
         * @param value The value to assign the option.
         *
         * @note Options are always case-sensitive.
         */
        """
        
        self.xsl_options[key] = value
        

    def convertToXHTML(self, filename):
        """
        /**
         * Converts the currently opened document to XHTML.
         *
         * This function does not modify the original document, but
         * modifications on the document will reflect on the result of
         * the conversion.
         *
         * You may want to call setXSLTransformation() and/or
         * setXSLOption() before calling this function to optimize the
         * result of the conversion for particular purposes.
         *
         * @param filename Filename of the resulting XHTML document.
         *
         * @return @c true if the document was successfully converted,
         *         @c false otherwise.
         *
         * @sa setXSLTransformation(), setXSLOption()
         */
        """
        
        if self.style is None:
            self.setXSLTransformation(self.xsl_transformation)
        
        # Prepare Preprocessor.
        if self.preprocessor is None:
            stylesheet = os.path.join(STYLESHEET_PATH, 'package2document.xsl')
            fp = file(stylesheet, 'rb')
            self.preprocessor_doc = lxml.etree.parse(fp)
            fp.close()
            self.preprocessor = lxml.etree.XSLT(self.preprocessor_doc)
        
        # Export objects.
        if self.xsl_options.get('export-objects', False) == 'true':
            self._exportObjects(os.path.dirname(filename))
        
        # Set preprocessor parameters.
        pp_args = {'mimetype': "'%s'" % self.mimetype,
                   'meta.xml': "'%s'" % os.path.join(self.tmp_dir, 'meta.xml'),
                   'settings.xml': "'%s'" % os.path.join(self.tmp_dir, 'settings.xml'),
                   'styles.xml': "'%s'" % os.path.join(self.tmp_dir, 'styles.xml'),
                  }
        
        # Preprocess.
        doc = self.preprocessor.apply(self.doc, **pp_args)
        
        #fp = file("/tmp/out.xml", "wb")
        #doc.write_c14n(fp)
        #fp.close()
        
        # Stylesheet transformation.
        result = self.style.apply(doc, **self.xsl_options)
        
        # Write result to file.
        fp = file(filename, 'wb')
        result.write_c14n(fp)
        fp.close()
        
        return True


    def scaleImages(self, maxWidth, maxHeight):
        """
        /**
         * Scales all images in the currently opened document to a
         * maximum resolution.
         *
         * @param maxWidth  The maximum width of the images.
         * @param maxHeight The maximum height of the images.
         *
         * @return @c true when all images could be successfully
         *         converted, @c false on error.
         *
         * @note Implementations may require ImageMagick to be installed
         *       to be able to work.
         */
        """
        
        raise NotImplementedError, 'scaleImages'
        
    
    def pathToContents(self):
        """
        /**
         * Returns the path to the directory in which you can find the
         * unzipped contents of the currently loaded OpenDocument file.
         *
         * @return The path to the temporary directory where the
         *         OpenDocument file has been unzipped to, or an empty
         *         string if no document is currently opened or if the
         *         currently opened document isn't an OpenDocument
         *         package but a plain XML file.
         */
        """
        
        if self.tmp_dir:
            return self.tmp_dir
        else:
            return ''


    def _exportObjects(self, directory):
        """
        Exports all images and replacements to the destination directory.
        """
        
        for f in ('ObjectReplacements', 'Pictures'):
            
            src = os.path.join(self.tmp_dir, f)
            dst = os.path.join(directory, f)
            
            if os.path.exists(src):
                if not os.path.exists(dst):
                    # Create destination.
                    os.mkdir(dst)
                
                for c in os.listdir(src):
                    # Copy files.
                    c = os.path.join(src, c)
                    copy_file(c, dst)


if __name__ == '__main__':
    """
    Commandline mode.
    """
    
    args = sys.argv[1:]
    
    if len(args) != 2:
        
        print >>sys.stderr, "Usage: OpenDocument.py OPENDOCUMENTFILE [OUTPUTFILE]"
        sys.exit(1)
        
    # Make instance.
    o = OpenDocument(args[0])
    
    # Convert.
    o.convertToXHTML(args[1])
    
    del o
    
