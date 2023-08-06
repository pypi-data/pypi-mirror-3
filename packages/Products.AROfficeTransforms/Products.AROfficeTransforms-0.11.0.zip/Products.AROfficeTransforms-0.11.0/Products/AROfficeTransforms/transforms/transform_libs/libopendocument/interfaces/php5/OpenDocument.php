<?php
/*
    OpenDocument.php, utility functions for working with OpenDocument files and
                      converting them to XHTML.
    Copyright (C) 2003-2006 Arend van Beelen jr., Auton Rijnsburg
                            <arend@auton.nl>

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
*/

define('LIBOPENDOCUMENT_PATH', AUKYLA_DIR.'/lib/opendocument');

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
	static public $dcNS     = 'http://purl.org/dc/elements/1.1/';
	static public $metaNS   = 'urn:oasis:names:tc:opendocument:xmlns:meta:1.0';
	static public $officeNS = 'urn:oasis:names:tc:opendocument:xmlns:office:1.0';

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
	public function __construct($filename = '')
	{
		$this->filename = '';
		$this->xslTransformation = 'default';
		$this->xslOptions = array('export-objects' => 'true',
		                          'position-image' => 'true');

		if($filename != '')
		{
			$this->open($filename);
		}
	}

	/**
	 * Destructor.
	 *
	 * Performs cleanup operations and closes the currently opened
	 * document if necessary.
	 *
	 * @sa close()
	 */
	public function __destruct()
	{
		if($this->filename != '')
		{
			$this->close();
		}
	}

	/**
	 * Opens the specified OpenDocument for use by the other utility
	 * functions in this class.
	 *
	 * @param filename Path to the OpenDocument file to load.
	 *
	 * @return @c true if the document was successfully loaded,
	 *         @c false otherwise.
	 */
	public function open($filename)
	{
		if($this->filename != '')
		{
			$this->close();
		}

		if(strcasecmp(substr($filename, -4), '.xml') == 0)
		{
			$this->package = false;

			$this->tmpdir = '';
		}
		else
		{
			$this->package = true;

			$this->tmpdir = tempnam('/tmp', 'OpenDocument');
			unlink($this->tmpdir);
			if(mkdir($this->tmpdir, 0700) == false)
			{
				trigger_error("Could not create temporary directory {$this->tmpdir}");
				return false;
			}
			if(copy($filename, "{$this->tmpdir}/document.od") == false)
			{
				exec("rm -R {$this->tmpdir}");
				trigger_error('Could not copy OpenDocument file');
				return false;
			}
			$output = array();
			exec("unzip {$this->tmpdir}/document.od -d {$this->tmpdir}", $output, $return);
			if($return != 0)
			{
				trigger_error("Could not unzip temporary document {$this->tmpdir}/document.od");
				exec("rm -R {$this->tmpdir}");
				return false;
			}
		}

		$this->filename = $filename;
		if($this->loadMeta() === false)
		{
			$this->filename = '';
			return false;
		}

		$this->xslOptions['title'] = $this->meta(self::$dcNS, 'title');

		return true;
	}

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
	public function save($filename = '')
	{
		$result = false;

		if($this->filename != '')
		{
			if($filename != '')
			{
				$this->filename = $filename;
			}

			if($this->package == false)
			{
				if($this->metaDocument->save($this->filename) !== false)
				{
					$result = true;
				}
			}
			else
			{
				$this->metaDocument->save("{$this->tmpdir}/meta.xml");

				exec("cd {$this->tmpdir}; rm document.od; zip -r - * > document.od", $output, $return);
				if($return == 0)
				{
					if(copy("{$this->tmpdir}/document.od", $this->filename) !== false)
					{
						$result = true;
					}
				}
			}
		}

		return $result;
	}

	/**
	 * Closes the currently opened document.
	 *
	 * Be sure to call save() before closing the document if you
	 * have made any modifications to the document you want to save.
	 *
	 * @sa save()
	 */
	public function close()
	{
		if($this->filename != '')
		{
			if($this->tmpdir != '')
			{
				exec("rm -R {$this->tmpdir}");
			}

			$this->filename = '';
			unset($this->metaDocument);
			unset($this->metaNode);
		}
	}

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
	public function meta($uri, $key)
	{
		if($this->metaNode->length == 0)
		{
			return '';
		}

		$metaNodes = $this->metaNode->item(0)->childNodes;

		for($i = 0; $i < $metaNodes->length; $i++)
		{
			$node = $metaNodes->item($i);

			if($node->namespaceURI == $uri &&
			   $node->localName == $key)
			{
				return $node->nodeValue;
			}
		}

		return '';
	}

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
	public function setMeta($uri, $key, $value)
	{
		if($this->metaNode->length == 0)
		{
			return false;
		}

		$metaNodes = $this->metaNode->item(0)->childNodes;

		for($i = 0; $i < $metaNodes->length; $i++)
		{
			$node = $metaNodes->item($i);

			if($node->namespaceURI == $uri &&
			   $node->localName == $key)
			{
				$node->nodeValue = $value;
				return true;
			}
		}

		$metaNode = $this->metaDocument->createElementNS($uri, $key, $value);
		$this->metaNode->item(0)->appendChild($metaNode);
		return true;
	}

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
	public function setXSLTransformation($name)
	{
		$this->xslTransformation = (string) $name;
	}

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
	public function setXSLOption($key, $value)
	{
		$this->xslOptions[(string) $key] = (string) $value;
	}

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
	public function convertToXHTML($filename)
	{
		if($this->filename == '')
		{
			trigger_error('No document was loaded for conversion to XHTML');
			return false;
		}

		$xslDocument = new DOMDocument();
		if($xslDocument->load(LIBOPENDOCUMENT_PATH."/xsl/{$this->xslTransformation}/document2xhtml.xsl") === false)
		{
			trigger_error('Could not open the selected XSL transformation');
			return false;
		}

		$xsltProcessor = new XSLTProcessor();
		if($xsltProcessor->hasExsltSupport() == false)
		{
			trigger_error('EXSLT support in PHP is required for converting OpenDocument files');
			return false;
		}

		if($this->package == false)
		{
			$sourceDocument = $this->metaDocument;
		}
		else
		{
			if($this->xslOptions['export-objects'] == 'true')
			{
				$this->exportObjects(dirname($filename));
			}

			$preprocessXSLDocument = new DOMDocument();
			if(copy(LIBOPENDOCUMENT_PATH."/xsl/package2document.xsl", "{$this->tmpdir}/package2document.xsl") === false ||
			   $preprocessXSLDocument->load("{$this->tmpdir}/package2document.xsl") === false)
			{
				trigger_error('Could not open the XSL transformation for pre-processing');
				return false;
			}

			$xsltProcessor->importStyleSheet($preprocessXSLDocument);

			$contentDocument = new DOMDocument();
			if($contentDocument->load("{$this->tmpdir}/content.xml") == false)
			{
				trigger_error('Could not load content XML document');
				return false;
			}

			$xsltProcessor->setParameter('', 'mimetype', file_get_contents("{$this->tmpdir}/mimetype"));

			$sourceDocument = $xsltProcessor->transformToDoc($contentDocument);
			if($sourceDocument === false)
			{
				trigger_error('Could not open source document');
				return false;
			}

			unlink("{$this->tmpdir}/package2document.xsl");
		}

		if(file_exists(LIBOPENDOCUMENT_PATH."/xsl/{$this->xslTransformation}/document2xhtml.php") == true)
		{
			include_once(LIBOPENDOCUMENT_PATH."/xsl/{$this->xslTransformation}/document2xhtml.php");
			OpenDocument2XHTML::init($this->xslOptions);
			$xsltProcessor->registerPHPFunctions();
		}

		$xsltProcessor->importStyleSheet($xslDocument);
		foreach($this->xslOptions as $key => $value)
		{
			$xsltProcessor->setParameter('', $key, $value);
		}

		if($xsltProcessor->transformToURI($sourceDocument, $filename) == false)
		{
			trigger_error('XSL transformation failed to run');
			return false;
		}

		return true;
	}

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
	 * @note ImageMagick is required for this function to work.
	 */
	public function scaleImages($maxWidth, $maxHeight)
	{
		if($this->filename == '')
		{
			trigger_error('No document was loaded for scaling images');
			return false;
		}
		if($this->package == false)
		{
			return true;
		}

		foreach(array('ObjectReplacements', 'Pictures') as $subdir)
		{
			if(file_exists("{$this->tmpdir}/$subdir") == false ||
			   ($dh = opendir("{$this->tmpdir}/$subdir")) === false)
			{
				continue;
			}

			while(($basename = readdir($dh)) !== false)
			{
				if($basename == '.' || $basename == '..')
				{
					continue;
				}

				$image = "{$this->tmpdir}/$subdir/$basename";

				unset($output);
				exec("identify ".escapeshellarg($image), $output, $return);
				if($return != 0)
				{
					trigger_error("Failed to run 'identify' on $basename, is ImageMagick installed?");
					continue;
				}

				list($format, $resolution) = explode(' ', substr($output[0], strlen($image) + 1));
				list($width, $height) = explode('x', $resolution);
				if($width > $maxWidth || $height > $maxHeight)
				{
					exec("mogrify -resize {$maxWidth}x{$maxHeight} ".escapeshellarg($image), $output, $return);
					if($return != 0)
					{
						trigger_error("Failed to run 'mogrify' on $basename, is ImageMagick installed?");
					}
				}
			}

			closedir($dh);
		}

		return true;
	}

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
	public function pathToContents()
	{
		if($this->filename == '')
		{
			trigger_error('Requesting path to contents while no document is loaded');
			return '';
		}

		return $this->tmpdir;
	}

	private function loadMeta()
	{
		if($this->package == true)
		{
			$file  = "{$this->tmpdir}/meta.xml";
			$query = '//office:document-meta/office:meta';
		}
		else
		{
			$file  = $this->filename;
			$query = '//office:document/office:meta';
		}

		$this->metaDocument = new DOMDocument();
		if($this->metaDocument->load($file) === false)
		{
			trigger_error('Could not parse XML contents in OpenDocument file');
			return false;
		}

		$xpath = new DOMXPath($this->metaDocument);
		$xpath->registerNamespace('dc',     self::$dcNS);
		$xpath->registerNamespace('meta',   self::$metaNS);
		$xpath->registerNamespace('office', self::$officeNS);

		$this->metaNode = $xpath->query($query);

		return true;
	}

	private function exportObjects($directory)
	{
		foreach(array('ObjectReplacements', 'Pictures') as $subdir)
		{
			if(file_exists("{$this->tmpdir}/$subdir") == false ||
			   ($dh = opendir("{$this->tmpdir}/$subdir")) === false)
			{
				continue;
			}

			$objectsDir = "$directory/$subdir";

			while(($basename = readdir($dh)) !== false)
			{
				if($basename == '.' || $basename == '..')
				{
					continue;
				}

				$object = "{$this->tmpdir}/$subdir/$basename";

				if(file_exists($objectsDir) == false)
				{
					mkdir($objectsDir);
				}
				copy($object, "$objectsDir/$basename");
			}

			closedir($dh);
		}
	}

	private $filename;
	private $package;
	private $tmpdir;
	private $metaDocument;
	private $metaNode;
	private $xslTransformation;
	private $xslOptions;
}

?>
