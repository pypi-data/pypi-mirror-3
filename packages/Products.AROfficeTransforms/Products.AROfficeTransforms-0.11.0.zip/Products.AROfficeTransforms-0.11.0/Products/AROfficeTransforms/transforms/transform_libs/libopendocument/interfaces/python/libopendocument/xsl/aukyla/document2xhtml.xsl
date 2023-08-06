<?xml version="1.0" encoding="utf-8"?>
<!--
     Content2XHTML.xsl, OpenDocument content.xml to XHTML converter
     Copyright (C) 2005-2006 Arend van Beelen, Auton Rijnsburg

     This program is free software; you can redistribute it and/or modify it
     under the terms of the GNU General Public License as published by the Free
     Software Foundation; either version 2 of the License, or (at your option)
     any later version.

     This program is distributed in the hope that it will be useful, but WITHOUT
     ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
     FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
     more details.

     You should have received a copy of the GNU General Public License along
     with this program; if not, write to the Free Software Foundation, Inc.,
     59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

     For any questions, comments or whatever, you may mail me at: arend@auton.nl
-->

<xsl:stylesheet version="1.0" xmlns="http://www.w3.org/1999/xhtml"
                              xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                              xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"
                              xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
                              xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
                              xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
                              xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0"
                              xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
                              xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
                              xmlns:xlink="http://www.w3.org/1999/xlink"
                              xmlns:php="http://php.net/xsl"
                              office:version="1.0"
                              exclude-result-prefixes="fo office style draw svg table text xlink php">

	<xsl:output method               = "xml"
	            encoding             = "utf-8"
	            media-type           = "application/xhtml+xml"
	            indent               = "no"
	            doctype-public       = "-//W3C//DTD XHTML 1.1//EN"
	            doctype-system       = "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd"
	            omit-xml-declaration = "no" />

	<xsl:strip-space elements="office:automatic-styles office:body office:document office:font-face-decls office:spreadsheet office:styles office:text" />

	<xsl:include href="Styles/FontFaceDecls.xsl" />
	<xsl:include href="Styles/Styles.xsl" />
	<xsl:include href="Styles/AutomaticStyles.xsl" />
	<xsl:include href="Content2XHTML/Draw.xsl" />
	<xsl:include href="Content2XHTML/Table.xsl" />
	<xsl:include href="Content2XHTML/Text.xsl" />

	<xsl:param name="object-prefix"></xsl:param>
	<xsl:param name="position-frames">true</xsl:param>
	<xsl:param name="ignore-font-name-and-size">false</xsl:param>
	<xsl:param name="ignore-cell-border-properties">false</xsl:param>
	<xsl:param name="ignore-list-properties">false</xsl:param>
	<xsl:param name="title"></xsl:param>

	<xsl:template match="/">
		<html>
			<xsl:apply-templates select="//office:document" />
		</html>
	</xsl:template>

	<xsl:template match="office:document">
		<head>
			<title><xsl:value-of select="$title"></xsl:value-of></title>
			<xsl:apply-templates select="//office:font-face-decls" />
			<xsl:apply-templates select="//office:styles" />
			<xsl:apply-templates select="//office:automatic-styles" />
		</head>
		<body>
			<xsl:apply-templates select="//office:body" />
		</body>
	</xsl:template>

	<xsl:template match="office:body">
		<xsl:apply-templates />
	</xsl:template>

	<xsl:template match="office:spreadsheet">
		<xsl:apply-templates />
	</xsl:template>

	<xsl:template match="office:text">
		<xsl:apply-templates />
	</xsl:template>

</xsl:stylesheet>
