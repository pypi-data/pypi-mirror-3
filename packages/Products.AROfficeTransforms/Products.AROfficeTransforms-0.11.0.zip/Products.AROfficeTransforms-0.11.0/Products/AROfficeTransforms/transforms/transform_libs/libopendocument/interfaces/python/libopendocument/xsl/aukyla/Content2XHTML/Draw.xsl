<?xml version="1.0" encoding="utf-8"?>
<!--
     Draw.xsl, Converts Draw elements in an OpenDocument format to XHTML
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

<xsl:stylesheet version="1.0" xmlns="http://www.w3.org/1999/xhtml"
                              xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                              xmlns:xlink="http://www.w3.org/1999/xlink"
                              xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
                              xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0"
                              xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">

	<xsl:strip-space elements="draw:frame draw:image svg:desc" />

	<xsl:template match="draw:frame">
		<xsl:choose>
			<xsl:when test="$position-frames='true'">
				<xsl:call-template name="insert-frame" />
			</xsl:when>
			<xsl:otherwise>
				<xsl:apply-templates/>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>

	<xsl:template match="draw:image">
		<img>
			<xsl:variable name="widthHeight">
				<xsl:if test="../@svg:width!=''">width: <xsl:value-of select="../@svg:width" />; </xsl:if>
				<xsl:if test="../@svg:height!=''">height: <xsl:value-of select="../@svg:height" />; </xsl:if>
				<xsl:if test="../@style:rel-width!=''">width: 100%; </xsl:if>
				<xsl:if test="../@style:rel-height!=''">height: 100%; </xsl:if>
				<xsl:if test="../@fo:min-width!=''">min-width: <xsl:value-of select="../@fo:min-width" />; </xsl:if>
				<xsl:if test="../@fo:min-height!=''">min-height: <xsl:value-of select="../@fo:min-height" />; </xsl:if>
			</xsl:variable>
			<xsl:attribute name="src">
				<xsl:choose>
					<xsl:when test="starts-with(@xlink:href, './')">
						<xsl:value-of select="concat($object-prefix, substring-after(@xlink:href, './'))" />
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="concat($object-prefix, @xlink:href)" />
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:attribute name="alt">
				<xsl:apply-templates select="svg:desc" />
			</xsl:attribute>
			<xsl:if test="$widthHeight!=''">
				<xsl:attribute name="style">
					<xsl:value-of select="$widthHeight" />
				</xsl:attribute>
			</xsl:if>
		</img>
	</xsl:template>

	<xsl:template match="svg:desc">
		<xsl:apply-templates/>
	</xsl:template>

	<xsl:template name="insert-frame">
		<div>
			<xsl:variable name="posStyle"><xsl:value-of select="php:function('OpenDocument2XHTML::style', 'graphic', string(@draw:style-name), 'text-align,vertical-align')" /></xsl:variable>
			<xsl:variable name="varStyle"><xsl:value-of select="php:function('OpenDocument2XHTML::style', 'graphic', string(@draw:style-name), 'margin,margin-top,margin-right,margin-bottom,margin-left,padding,padding-top,padding-right,padding-bottom,padding-left,border,border-top,border-right,border-bottom,border-left,background-color')" /></xsl:variable>
			<xsl:variable name="widthHeight">
				<xsl:if test="@svg:width!=''">width: <xsl:value-of select="@svg:width" />; </xsl:if>
				<xsl:if test="@svg:height!=''">height: <xsl:value-of select="@svg:height" />; </xsl:if>
				<xsl:if test="@style:rel-width!=''">width: <xsl:value-of select="@style:rel-width" />; </xsl:if>
				<xsl:if test="@style:rel-height!=''">height: <xsl:value-of select="@style:rel-height" />; </xsl:if>
				<xsl:if test="@fo:min-width!=''">min-width: <xsl:value-of select="@fo:min-width" />; </xsl:if>
				<xsl:if test="@fo:min-height!=''">min-height: <xsl:value-of select="@fo:min-height" />; </xsl:if>
			</xsl:variable>
			<xsl:choose>
				<xsl:when test="@text:anchor-type='as-char'">
					<xsl:attribute name="style">display: -moz-inline-box; display: inline-block</xsl:attribute>
					<div>
						<xsl:attribute name="style"><xsl:value-of select="$varStyle" /></xsl:attribute>
						<xsl:apply-templates/>
					</div>
				</xsl:when>
				<xsl:when test="@text:anchor-type='char' or @text:anchor-type='paragraph'">
					<xsl:attribute name="style"><xsl:value-of select="$posStyle" /></xsl:attribute>
					<div>
						<xsl:attribute name="style">display: -moz-inline-box; display: inline-block; <xsl:value-of select="$widthHeight" />z-index: <xsl:value-of select="@draw:z-index" />; <xsl:value-of select="$varStyle" /></xsl:attribute>
						<div>
							<xsl:attribute name="style">text-align: left</xsl:attribute>
							<xsl:apply-templates/>
						</div>
					</div>
				</xsl:when>
				<xsl:otherwise>
					<xsl:apply-templates/>
				</xsl:otherwise>
			</xsl:choose>
		</div>
	</xsl:template>

</xsl:stylesheet>
