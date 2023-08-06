<?xml version="1.0" encoding="utf-8"?>
<!--
     Table.xsl, Converts Table elements in an OpenDocument format to XHTML
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
                              xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0">

	<xsl:strip-space elements="table:table table:table-cell table:table-column table:table-header-rows table:table-row" />

	<xsl:template match="table:table">
		<table>
			<xsl:choose>
				<xsl:when test="$ignore-cell-border-properties='true'">
					<xsl:attribute name="border">1</xsl:attribute>
				</xsl:when>
				<xsl:otherwise>
					<xsl:attribute name="cellpadding">0</xsl:attribute>
					<xsl:attribute name="cellspacing">0</xsl:attribute>
				</xsl:otherwise>
			</xsl:choose>
			<xsl:call-template name="insert-table-style" />
			<xsl:if test="@table:is-sub-table='true'">
				<xsl:attribute name="style">width: 100%</xsl:attribute>
			</xsl:if>
			<colgroup>
				<xsl:apply-templates select="table:table-column" />
			</colgroup>
			<thead>
				<xsl:apply-templates select="table:table-header-rows" />
			</thead>
			<tbody>
				<xsl:apply-templates select="table:table-row" />
			</tbody>
		</table>
	</xsl:template>

	<xsl:template match="table:table-column">
		<col>
			<xsl:call-template name="insert-table-column-style" />
			<xsl:if test="@table:number-columns-repeated!=''">
				<xsl:attribute name="span"><xsl:value-of select="@table:number-columns-repeated" /></xsl:attribute>
			</xsl:if>
			<xsl:apply-templates />
		</col>
	</xsl:template>

	<xsl:template match="table:table-header-rows">
		<xsl:apply-templates select="table:table-row" />
	</xsl:template>

	<xsl:template match="table:table-row">
		<tr>
			<xsl:call-template name="insert-table-row-style" />
			<xsl:apply-templates />
		</tr>
	</xsl:template>

	<xsl:template match="table:table-cell">
		<td>
			<xsl:call-template name="insert-table-cell-style" />
			<xsl:if test="@table:number-columns-spanned!=''">
				<xsl:attribute name="colspan"><xsl:value-of select="@table:number-columns-spanned" /></xsl:attribute>
			</xsl:if>
			<xsl:apply-templates />
			<xsl:if test="count(./*)=0">
				<br />
			</xsl:if>
		</td>
		<xsl:if test="@table:number-columns-repeated!=''">
			<xsl:call-template name="repeated-table-cell" />
		</xsl:if>
	</xsl:template>

	<xsl:template name="repeated-table-cell">
		<xsl:param name="currentCol">1</xsl:param>
		<td>
			<xsl:call-template name="insert-table-cell-style">
				<xsl:with-param name="currentCol"><xsl:value-of select="$currentCol" /></xsl:with-param>
			</xsl:call-template>
			<xsl:apply-templates />
			<xsl:if test="count(./*)=0">
				<br />
			</xsl:if>
		</td>
		<xsl:if test="$currentCol &lt; @table:number-columns-repeated - 1">
			<xsl:call-template name="repeated-table-cell">
				<xsl:with-param name="currentCol"><xsl:value-of select="$currentCol + 1" /></xsl:with-param>
			</xsl:call-template>
		</xsl:if>
	</xsl:template>

	<xsl:template name="insert-table-style">
		<xsl:variable name="style" select="php:function('OpenDocument2XHTML::style', 'table', string(@table:style-name))" />
		<xsl:if test="$style!=''">
			<xsl:attribute name="style">
				<xsl:value-of select="$style" />
			</xsl:attribute>
		</xsl:if>
	</xsl:template>

	<xsl:template name="insert-table-column-style">
		<xsl:variable name="style" select="php:function('OpenDocument2XHTML::style', 'table-column', string(@table:style-name))" />
		<xsl:if test="$style!=''">
			<xsl:attribute name="style">
				<xsl:value-of select="$style" />
			</xsl:attribute>
		</xsl:if>
	</xsl:template>

	<xsl:template name="insert-table-row-style">
		<xsl:variable name="style" select="php:function('OpenDocument2XHTML::style', 'table-row', string(@table:style-name))" />
		<xsl:if test="$style!=''">
			<xsl:attribute name="style">
				<xsl:value-of select="$style" />
			</xsl:attribute>
		</xsl:if>
	</xsl:template>

	<xsl:template name="insert-table-cell-style">
		<xsl:param name="currentCol">0</xsl:param>
		<xsl:variable name="style" select="php:function('OpenDocument2XHTML::style', 'table-cell', string(@table:style-name))" />
		<xsl:if test="$style!=''">
			<xsl:attribute name="style">
				<xsl:value-of select="$style" />
			</xsl:attribute>
		</xsl:if>
		<xsl:if test="$style=''">
			<xsl:variable name="curPosition" select="position() + $currentCol + sum(preceding-sibling::table:table-cell/@table:number-columns-repeated) - count(preceding-sibling::table:table-cell/@table:number-columns-repeated)" />
			<xsl:variable name="defaultStyle" select="php:function('OpenDocument2XHTML::style', 'table-cell', string(../../table:table-column[$curPosition]/@table:default-cell-style-name))" />
			<xsl:if test="$defaultStyle!=''">
				<xsl:attribute name="style">
					<xsl:value-of select="$defaultStyle" />
				</xsl:attribute>
			</xsl:if>
		</xsl:if>
	</xsl:template>

</xsl:stylesheet>
