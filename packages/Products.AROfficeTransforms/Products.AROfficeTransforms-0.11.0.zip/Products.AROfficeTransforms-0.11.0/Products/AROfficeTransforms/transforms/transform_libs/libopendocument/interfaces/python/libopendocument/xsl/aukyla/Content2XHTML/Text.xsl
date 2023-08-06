<?xml version="1.0" encoding="utf-8"?>
<!--
     Text.xsl, Converts Text elements in an OpenDocument format to XHTML
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
                              xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
                              xmlns:xlink="http://www.w3.org/1999/xlink"
                              xmlns:php="http://php.net/xsl">

	<xsl:strip-space elements="text:h text:list text:list-item text:p text:span" />

	<xsl:template match="text:h">
		<xsl:choose>
			<xsl:when test="@text:outline-level='1'">
				<h1>
					<xsl:call-template name="insert-paragraph-style" />
					<xsl:apply-templates />
				</h1>
			</xsl:when>
			<xsl:when test="@text:outline-level='2'">
				<h2>
					<xsl:call-template name="insert-paragraph-style" />
					<xsl:apply-templates />
				</h2>
			</xsl:when>
			<xsl:when test="@text:outline-level='3'">
				<h3>
					<xsl:call-template name="insert-paragraph-style" />
					<xsl:apply-templates />
				</h3>
			</xsl:when>
			<xsl:when test="@text:outline-level='4'">
				<h4>
					<xsl:call-template name="insert-paragraph-style" />
					<xsl:apply-templates />
				</h4>
			</xsl:when>
			<xsl:when test="@text:outline-level='5'">
				<h5>
					<xsl:call-template name="insert-paragraph-style" />
					<xsl:apply-templates />
				</h5>
			</xsl:when>
			<xsl:when test="@text:outline-level='6'">
				<h6>
					<xsl:call-template name="insert-paragraph-style" />
					<xsl:apply-templates />
				</h6>
			</xsl:when>
			<xsl:otherwise>
				<span>
					<xsl:call-template name="insert-paragraph-style" />
					<xsl:apply-templates />
				</span>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>

	<xsl:template match="text:p">
		<div>
			<xsl:choose>
				<xsl:when test="name(..)='text:list-item'">
					<xsl:variable name="listLevel" select="count(ancestor::text:list)" />
					<xsl:variable name="totalWidth" select="substring-after(php:function('OpenDocument2XHTML::listStyle', string(ancestor::text:list[@text:style-name!='']/@text:style-name), string($listLevel), 'total-width'), 'total-width: ')" />
					<xsl:call-template name="insert-paragraph-style">
						<xsl:with-param name="addCss">margin-left: <xsl:value-of select="$totalWidth" />; </xsl:with-param>
					</xsl:call-template>
					<xsl:apply-templates />
				</xsl:when>
				<xsl:otherwise>
					<xsl:call-template name="insert-paragraph-style" />
					<xsl:apply-templates />
					<xsl:if test=".=''">
						<br />
					</xsl:if>
				</xsl:otherwise>
			</xsl:choose>
		</div>
	</xsl:template>

	<xsl:template match="text:list">
		<ul>
			<xsl:call-template name="insert-list-style" />
			<xsl:apply-templates />
		</ul>
	</xsl:template>

	<xsl:template match="text:list-item">
		<li>
			<xsl:call-template name="insert-custom-style-type" />
			<xsl:if test="../@text:continue-numbering='true' and count(preceding-sibling::text:list-item) = 0">
				<xsl:attribute name="value">
					<xsl:call-template name="calculate-list-items-before">
						<xsl:with-param name="currentPosition"><xsl:value-of select="count(../preceding-sibling::text:list) + 1" /></xsl:with-param>
					</xsl:call-template>
				</xsl:attribute>
			</xsl:if>
			<xsl:apply-templates />
		</li>
	</xsl:template>

	<xsl:template match="text:line-break">
		<br />
	</xsl:template>

	<xsl:template match="text:span">
		<span>
			<xsl:call-template name="insert-text-style" />
			<xsl:apply-templates />
		</span>
	</xsl:template>

	<xsl:template match="text:tab">
		<xsl:choose>
			<xsl:when test="(count(ancestor::text:alphabetical-index) > 0) or (count(ancestor::text:table-of-content) > 0)">
				<xsl:text> . . . . . . . . . . </xsl:text>
			</xsl:when>
			<xsl:otherwise>
				<span style="margin-left: 1.1cm" />
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>

	<xsl:template match="text:s">
		<xsl:choose>
			<xsl:when test="@text:c!=''">
				<xsl:call-template name="insert-nbsp">
					<xsl:with-param name="c"><xsl:value-of select="@text:c" /></xsl:with-param>
				</xsl:call-template>
			</xsl:when>
			<xsl:otherwise>
				<xsl:call-template name="insert-nbsp" />
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>

	<xsl:template name="insert-nbsp">
		<xsl:param name="c" default="1" />
		<xsl:value-of disable-output-escaping="yes" select="'&amp;nbsp;'"/>
		<xsl:if test="$c > 1">
			<xsl:call-template name="insert-nbsp">
				<xsl:with-param name="c"><xsl:value-of select="$c - 1" /></xsl:with-param>
			</xsl:call-template>
		</xsl:if>
	</xsl:template>

	<xsl:template match="text:a">
		<a>
			<xsl:attribute name="href">
				<xsl:value-of select="@xlink:href" />
			</xsl:attribute>
			<xsl:call-template name="insert-text-style" />
			<xsl:apply-templates />
		</a>
	</xsl:template>

	<xsl:template match="text:alphabetical-index-source">
	</xsl:template>

	<xsl:template match="text:table-of-content-source">
	</xsl:template>

	<xsl:template name="calculate-list-items-before">
		<xsl:param name="currentPosition" default="1" />
		<xsl:choose>
			<xsl:when test="../../text:list[position() = ($currentPosition - 1)]/@text:continue-numbering='true'">
				<xsl:variable name="currentNumber">
					<xsl:value-of select="count(../../text:list[position()=($currentPosition - 1)]/text:list-item)" />
				</xsl:variable>
				<xsl:variable name="previousNumber">
					<xsl:call-template name="calculate-list-items-before">
						<xsl:with-param name="currentPosition"><xsl:value-of select="$currentPosition - 1" /></xsl:with-param>
					</xsl:call-template>
				</xsl:variable>
				<xsl:value-of select="number($currentNumber) + number($previousNumber)" />
			</xsl:when>
			<xsl:otherwise>
				<xsl:value-of select="count(../../text:list[position()=($currentPosition - 1)]/text:list-item) + 1" />
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>

	<xsl:template name="insert-text-style">
		<xsl:variable name="style" select="php:function('OpenDocument2XHTML::style', 'text', string(@text:style-name))" />
		<xsl:if test="$style!=''">
			<xsl:attribute name="style"><xsl:value-of select="$style" /></xsl:attribute>
		</xsl:if>
	</xsl:template>

	<xsl:template name="insert-paragraph-style">
		<xsl:param name="addCss" default="" />
		<xsl:variable name="style" select="php:function('OpenDocument2XHTML::style', 'paragraph', string(@text:style-name))" />
		<xsl:if test="$addCss!='' or $style!=''">
			<xsl:attribute name="style"><xsl:value-of select="$addCss" /><xsl:value-of select="$style" /></xsl:attribute>
		</xsl:if>
	</xsl:template>

	<xsl:template name="insert-list-style">
		<xsl:choose>
			<xsl:when test="($ignore-list-properties='true') and (name(..)='text:list-item') and (count(../child::*[name(.)!='text:list'])=0)">
				<xsl:attribute name="style">margin-top: -1.2em</xsl:attribute>
			</xsl:when>
			<xsl:otherwise>
				<xsl:if test="$ignore-list-properties='true'">
					<xsl:attribute name="style">margin-top: 0px; margin-bottom: 0px</xsl:attribute>
				</xsl:if>
				<xsl:variable name="listLevel" select="count(ancestor-or-self::text:list)" />
				<xsl:for-each select="ancestor-or-self::text:list">
					<xsl:variable name="style" select="php:function('OpenDocument2XHTML::listStyle', string(@text:style-name), string($listLevel))" />
					<xsl:if test="$style!=''">
						<xsl:choose>
							<xsl:when test="contains($style, 'list-style-type: custom')">
								<xsl:attribute name="style">display: block; padding: 0px; margin: 0px</xsl:attribute>
							</xsl:when>
							<xsl:otherwise>
								<xsl:attribute name="style">
									<xsl:if test="$ignore-list-properties='true'">margin-top: 0px; margin-bottom: 0px; </xsl:if>
									<xsl:value-of select="$style" />
								</xsl:attribute>
							</xsl:otherwise>
						</xsl:choose>
					</xsl:if>
				</xsl:for-each>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>

	<xsl:template name="insert-custom-style-type">
		<xsl:choose>
			<xsl:when test="count(./child::*[name(.)!='text:list'])>0">
				<xsl:variable name="listLevel" select="count(ancestor::text:list)" />
				<xsl:variable name="listStyleType" select="php:function('OpenDocument2XHTML::listStyle', string(ancestor::text:list[@text:style-name!='']/@text:style-name), string($listLevel), 'list-style-type')" />
				<xsl:choose>
					<xsl:when test="starts-with($listStyleType, 'list-style-type: custom')">
						<xsl:attribute name="style">display: block; clear: both; padding: 0px; margin: 0px</xsl:attribute>
						<div>
							<xsl:attribute name="style">float: left; <xsl:value-of select="php:function('OpenDocument2XHTML::listStyle', string(ancestor::text:list[@text:style-name!='']/@text:style-name), string($listLevel), 'margin-left,min-width')" /></xsl:attribute>
							<xsl:value-of select="substring-after($listStyleType, 'list-style-type: custom ')" />
						</div>
					</xsl:when>
					<xsl:otherwise>
						<xsl:attribute name="style">margin-top: 0px; margin-bottom: 0px</xsl:attribute>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:when>
			<xsl:otherwise>
				<xsl:attribute name="style">display: block; list-style-type: none; padding: 0px; margin: 0px</xsl:attribute>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>

</xsl:stylesheet>
