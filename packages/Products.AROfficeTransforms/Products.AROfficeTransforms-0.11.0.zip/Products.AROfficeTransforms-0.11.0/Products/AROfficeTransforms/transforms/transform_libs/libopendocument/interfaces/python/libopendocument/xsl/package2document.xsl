<?xml version="1.0" encoding="utf-8"?>
<!--
     package2document.xsl, converts separate XML files from an OpenDocument
                           package to a single XML document
     Copyright (C) 2005 Arend van Beelen, Auton Rijnsburg

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

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                              xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
                              xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0"
                              xmlns:config="urn:oasis:names:tc:opendocument:xmlns:config:1.0"
                              xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
                              xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
                              xmlns:drawing="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
                              xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0"
                              xmlns:dr3d="urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0"
                              xmlns:anim="urn:oasis:names:tc:opendocument:xmlns:animation:1.0"
                              xmlns:chart="urn:oasis:names:tc:opendocument:xmlns:chart:1.0"
                              xmlns:form="urn:oasis:names:tc:opendocument:xmlns:form:1.0"
                              xmlns:script="urn:oasis:names:tc:opendocument:xmlns:script:1.0"
                              xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
                              xmlns:number="urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0"
                              xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"
                              xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0"
                              xmlns:smil="urn:oasis:names:tc:opendocument:xmlns:smil-compatible:1.0"
                              xmlns:dc="http://purl.org/dc/elements/1.1/"
                              xmlns:xlink="http://www.w3.org/1999/xlink"
                              xmlns:math="http://www.w3.org/1998/Math/MathML"
                              xmlns:xforms="http://www.w3.org/2002/xforms"
                              office:version="1.0">

	<xsl:output method               = "xml"
	            encoding             = "utf-8"
	            indent               = "no"
	            omit-xml-declaration = "no" />

	<xsl:param name="mimetype"></xsl:param>
	<xsl:param name="meta.xml">meta.xml</xsl:param>
	<xsl:param name="settings.xml">settings.xml</xsl:param>
	<xsl:param name="styles.xml">styles.xml</xsl:param>

	<xsl:template match="/">
		<office:document>
			<xsl:attribute name="office:mimetype"><xsl:value-of select="$mimetype" /></xsl:attribute>
			<office:meta>
				<xsl:apply-templates select="document($meta.xml)/office:document-meta/office:meta" />
			</office:meta>
			<office:settings>
				<xsl:apply-templates select="document($settings.xml)/office:document-settings/office:settings" />
			</office:settings>
			<office:scripts>
				<xsl:apply-templates select="//office:document-content/office:scripts" />
			</office:scripts>
			<office:font-face-decls>
				<xsl:apply-templates select="document($styles.xml)/office:document-styles/office:font-face-decls" />
				<xsl:apply-templates select="//office:document-content/office:font-face-decls" />
			</office:font-face-decls>
			<office:styles>
				<xsl:apply-templates select="document($styles.xml)/office:document-styles/office:styles" />
			</office:styles>
			<office:automatic-styles>
				<xsl:apply-templates select="document($styles.xml)/office:document-styles/office:automatic-styles" />
				<xsl:apply-templates select="//office:document-content/office:automatic-styles" />
			</office:automatic-styles>
			<office:master-styles>
				<xsl:apply-templates select="document($styles.xml)/office:document-styles/office:master-styles" />
			</office:master-styles>
			<office:body>
				<xsl:apply-templates select="//office:document-content/office:body" />
			</office:body>
		</office:document>
	</xsl:template>

	<xsl:template match="*">
		<xsl:copy-of select="*" />
	</xsl:template>

</xsl:stylesheet>
