<?xml version="1.0" encoding="utf-8"?>
<!--
     FontFaceDecls.xsl
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
                              xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
                              xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0"
                              xmlns:php="http://php.net/xsl">

	<xsl:template match="office:font-face-decls">
		<xsl:apply-templates />
	</xsl:template>

	<xsl:template match="style:font-face">
		<xsl:value-of select="php:function('OpenDocument2XHTML::setFontFace', string(@style:name), string(@svg:font-family))" />
	</xsl:template>

</xsl:stylesheet>
