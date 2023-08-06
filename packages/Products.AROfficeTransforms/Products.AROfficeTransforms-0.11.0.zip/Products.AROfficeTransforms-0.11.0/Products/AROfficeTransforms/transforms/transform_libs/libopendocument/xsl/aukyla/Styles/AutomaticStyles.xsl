<?xml version="1.0" encoding="utf-8"?>
<!--
     AutomaticStyles.xsl
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
                              xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"
                              xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
                              xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
                              xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
                              xmlns:php="http://php.net/xsl">

	<xsl:template match="office:automatic-styles">
		<xsl:apply-templates />
	</xsl:template>

	<xsl:template match="style:default-style">
		<xsl:value-of select="php:function('OpenDocument2XHTML::createStyle',
		                                   string(@style:family),
		                                   '',
		                                   string(@style:parent-style-name))" />
		<xsl:apply-templates />
	</xsl:template>

	<xsl:template match="style:style">
		<xsl:value-of select="php:function('OpenDocument2XHTML::createStyle',
		                                   string(@style:family),
		                                   string(@style:name),
		                                   string(@style:parent-style-name))" />
		<xsl:apply-templates />
	</xsl:template>

	<xsl:template match="text:list-style">
		<xsl:value-of select="php:function('OpenDocument2XHTML::createListStyle',
		                                   string(@style:name))" />
		<xsl:apply-templates />
	</xsl:template>

	<xsl:template match="style:text-properties">
		<xsl:value-of select="php:function('OpenDocument2XHTML::setStyleTextProperties',
		                                   string(../@style:family),
		                                   string(../@style:name),
		                                   string(@style:font-name),
		                                   string(@fo:font-size),
		                                   string(@fo:font-style),
		                                   string(@fo:font-weight),
		                                   string(@style:text-underline-style),
		                                   string(@fo:color),
		                                   string(@fo:background-color),
		                                   string(@style:text-position))" />
	</xsl:template>

	<xsl:template match="style:paragraph-properties">
		<xsl:value-of select="php:function('OpenDocument2XHTML::setStyleParagraphProperties',
		                                   string(../@style:family),
		                                   string(../@style:name),
		                                   string(@fo:margin-top),
		                                   string(@fo:margin-right),
		                                   string(@fo:margin-bottom),
		                                   string(@fo:margin-left),
		                                   string(@fo:text-indent),
		                                   string(@fo:text-align))" />
	</xsl:template>

	<xsl:template match="style:table-properties">
		<xsl:value-of select="php:function('OpenDocument2XHTML::setStyleTableProperties',
		                                   string(../@style:family),
		                                   string(../@style:name),
		                                   string(@style:width))" />
	</xsl:template>

	<xsl:template match="style:table-column-properties">
		<xsl:value-of select="php:function('OpenDocument2XHTML::setStyleTableColumnProperties',
		                                   string(../@style:family),
		                                   string(../@style:name),
		                                   string(@style:column-width))" />
	</xsl:template>

	<xsl:template match="style:table-row-properties">
		<xsl:value-of select="php:function('OpenDocument2XHTML::setStyleTableRowProperties',
		                                   string(../@style:family),
		                                   string(../@style:name),
		                                   string(@style:row-height))" />
	</xsl:template>

	<xsl:template match="style:table-cell-properties">
		<xsl:value-of select="php:function('OpenDocument2XHTML::setStyleTableCellProperties',
		                                   string(../@style:family),
		                                   string(../@style:name),
		                                   string(@fo:margin),
		                                   string(@fo:margin-top),
		                                   string(@fo:margin-right),
		                                   string(@fo:margin-bottom),
		                                   string(@fo:margin-left),
		                                   string(@fo:padding),
		                                   string(@fo:padding-top),
		                                   string(@fo:padding-right),
		                                   string(@fo:padding-bottom),
		                                   string(@fo:padding-left),
		                                   string(@fo:border),
		                                   string(@fo:border-top),
		                                   string(@fo:border-right),
		                                   string(@fo:border-bottom),
		                                   string(@fo:border-left),
		                                   string(@fo:background-color))" />
	</xsl:template>

	<xsl:template match="text:list-level-style-number">
		<xsl:value-of select="php:function('OpenDocument2XHTML::setStyleListProperties',
		                                   string(../@style:name),
		                                   string(@text:level),
		                                   '',
		                                   string(@style:num-format),
		                                   string(style:list-level-properties/@text:space-before),
		                                   string(style:list-level-properties/@text:min-label-width))" />
	</xsl:template>

	<xsl:template match="text:list-level-style-bullet">
		<xsl:value-of select="php:function('OpenDocument2XHTML::setStyleListProperties',
		                                   string(../@style:name),
		                                   string(@text:level),
		                                   string(@text:bullet-char),
		                                   '',
		                                   string(style:list-level-properties/@text:space-before),
		                                   string(style:list-level-properties/@text:min-label-width))" />
	</xsl:template>

	<xsl:template match="style:graphic-properties">
		<xsl:value-of select="php:function('OpenDocument2XHTML::setStyleGraphicProperties',
		                                   string(../@style:family),
		                                   string(../@style:name),
		                                   '',
		                                   string(@style:vertical-pos),
		                                   string(@style:horizontal-pos))" />
		<xsl:value-of select="php:function('OpenDocument2XHTML::setStyleTableCellProperties',
		                                   string(../@style:family),
		                                   string(../@style:name),
		                                   string(@fo:margin),
		                                   string(@fo:margin-top),
		                                   string(@fo:margin-right),
		                                   string(@fo:margin-bottom),
		                                   string(@fo:margin-left),
		                                   string(@fo:padding),
		                                   string(@fo:padding-top),
		                                   string(@fo:padding-right),
		                                   string(@fo:padding-bottom),
		                                   string(@fo:padding-left),
		                                   string(@fo:border),
		                                   string(@fo:border-top),
		                                   string(@fo:border-right),
		                                   string(@fo:border-bottom),
		                                   string(@fo:border-left),
		                                   string(@fo:background-color))" />
	</xsl:template>

</xsl:stylesheet>
