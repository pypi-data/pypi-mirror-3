/*
    libopendocument.h
    Copyright (C) 2006 Arend van Beelen jr., Auton Rijnsburg

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

    Author: Arend van Beelen jr.
    Contact: arend@auton.nl
*/

#ifndef LIBOPENDOCUMENT_H
#define LIBOPENDOCUMENT_H

#include <string>

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
class OpenDocument
{
	public:
		static const char *dcNS     = "http://purl.org/dc/elements/1.1/";
		static const char *metaNS   = "urn:oasis:names:tc:opendocument:xmlns:meta:1.0";
		static const char *officeNS = "urn:oasis:names:tc:opendocument:xmlns:office:1.0";

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
		explicit OpenDocument(std::string filename = "");

		/**
		 * Destructor.
		 *
		 * Performs cleanup operations and closes the currently opened
		 * document if necessary.
		 *
		 * @sa close()
		 */
		~OpenDocument();

		/**
		 * Opens the specified OpenDocument for use by the other utility
		 * functions in this class.
		 *
		 * @param filename Path to the OpenDocument file to load.
		 *
		 * @return @c true if the document was successfully loaded,
		 *         @c false otherwise.
		 */
		bool open(std::string filename);

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
		bool save(std::string filename = "");

		/**
		 * Closes the currently opened document.
		 *
		 * Be sure to call save() before closing the document if you
		 * have made any modifications to the document you want to save.
		 *
		 * @sa save()
		 */
		void close();

		/**
		 * Returns the value of a meta data attribute in the currently
		 * opened document.
		 *
		 * @param uri The namespace URI of the meta data attribute.
		 * @param key The node name of the meta data attribute.
		 * @return The value of the meta data attribute. This may be an
		 *         empty string if the attribute is not defined.
		 *
		 * @sa setMeta()
		 */
		std::string meta(std::string uri, std::string key) const;

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
		bool setMeta(std::string uri, std::string key, std::string value);

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
		void setXSLTransformation(std::string name);

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
		 * Option: "export-objects"
		 * Possible values: "true", "false"
		 * Default value: "true"
		 * Description: By default, all objects (images, OLE object
		 *              replacements) contained within the OpenDocument
		 *              file will be exported, together with the
		 *              directory they reside in, to the same directory
		 *              as the resulting XHTML file upon conversion. By
		 *              setting this option to "false", no objects are
		 *              exported.
		 *
		 * The following options are also expected to be supported by the
		 * XSL sheets:
		 *
		 * Option: "title"
		 * Possible values: Any string
		 * Default value: The title as set in the meta-data of the source
		 *                document
		 * Description: The title is set in the output document inside
		 *              the \<title\> tag.
		 *
		 * Option: "object-prefix"
		 * Possible values: Any string
		 * Default value:  ""
		 * Description: Any references to objects like images or OLE
		 *              objects are given as a relative path, like for
		 *              instance "Pictures/000123.png". Using this
		 *              option, you can prepend anything in front of this
		 *              path to make it an absolute path or modify the
		 *              relative path.
		 *
		 * @param key   The name of the option to set.
		 * @param value The value to assign the option.
		 *
		 * @note Options are always case-sensitive.
		 */
		void setXSLOption(std::string key, std::string value);

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
		bool convertToXHTML(std::string filename) const;

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
		bool scaleImages(unsigned int maxWidth, unsigned int maxHeight);

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
		std::string pathToContents() const;
};

#endif // LIBOPENDOCUMENT_H
