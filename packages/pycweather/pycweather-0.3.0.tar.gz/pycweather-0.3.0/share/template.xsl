<?xml version="1.0" encoding="UTF-8"?>
<!-- pycweather/template.xsl: XSL stylesheet for displaying weather

This file is part of PycWeather

Copyright (c) 2009-2011 Vlad Glagolev <enqlave@gmail.com>. All rights reserved.

Permission to use, copy, modify, and distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

-->
<xsl:stylesheet xmlns="http://www.w3.org/1999/xhtml" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
	<xsl:output method="text" disable-output-escaping="yes"/>
	<!-- new line -->
	<xsl:variable name="nl">
		<xsl:text>&#10;</xsl:text>
	</xsl:variable>
	<!-- extract image ID -->
	<xsl:template name="getCondition">
		<xsl:param name="filename"/>
		<xsl:choose>
			<xsl:when test="contains($filename, '/')">
				<xsl:call-template name="getCondition">
					<xsl:with-param name="filename" select="substring-after($filename, '/')"/>
				</xsl:call-template>
			</xsl:when>
			<xsl:otherwise>
				<xsl:value-of select="$filename"/>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>
	<!-- main block -->
	<xsl:template match="channel">
		<xsl:comment>PycWeather 0.3.0</xsl:comment>
		<xsl:text>Location: </xsl:text><xsl:value-of select="normalize-space(substring-before(title, '- AccuWeather.com'))"/><xsl:value-of select="$nl"/>
		<xsl:text>Update Time: </xsl:text><xsl:value-of select="pubDate"/>
		<!-- don't parse info field -->
		<xsl:apply-templates select="child::item[position() != last()]"/>
	</xsl:template>
	<!-- day field -->
	<xsl:template match="item">
		<xsl:value-of select="$nl"/>
		<xsl:variable name="condition">
			<xsl:call-template name="getCondition">
				<xsl:with-param name="filename" select="substring-before(description, '_')"/>
			</xsl:call-template>
		</xsl:variable>
		<!-- convert image ID to ConkyWeather font character -->
		<xsl:choose>
			<xsl:when test="number($condition) = 1">
				<xsl:text>a</xsl:text>
			</xsl:when>
			<xsl:when test="number($condition) = 2">
				<xsl:text>b</xsl:text>
			</xsl:when>
			<xsl:when test="number($condition) = 3">
				<xsl:text>c</xsl:text>
			</xsl:when>
			<xsl:when test="number($condition) = 4">
				<xsl:text>c</xsl:text>
			</xsl:when>
			<xsl:when test="number($condition) = 5">
				<xsl:text>c</xsl:text>
			</xsl:when>
			<xsl:when test="number($condition) = 6">
				<xsl:text>d</xsl:text>
			</xsl:when>
			<xsl:when test="number($condition) = 7">
				<xsl:text>e</xsl:text>
			</xsl:when>
			<xsl:when test="number($condition) = 8">
				<xsl:text>e</xsl:text>
			</xsl:when>
			<xsl:when test="$condition = 11">
				<xsl:text>0</xsl:text>
			</xsl:when>
			<xsl:when test="$condition = 12">
				<xsl:text>h</xsl:text>
			</xsl:when>
			<xsl:when test="$condition = 13 or $condition = 14">
				<xsl:text>g</xsl:text>
			</xsl:when>
			<xsl:when test="$condition = 15">
				<xsl:text>l</xsl:text>
			</xsl:when>
			<xsl:when test="$condition = 16 or $condition = 17">
				<xsl:text>k</xsl:text>
			</xsl:when>
			<xsl:when test="$condition = 18 or $condition = 26">
				<xsl:text>i</xsl:text>
			</xsl:when>
			<xsl:when test="$condition = 19">
				<xsl:text>p</xsl:text>
			</xsl:when>
			<xsl:when test="$condition = 20 or $condition = 21 or $condition = 23">
				<xsl:text>o</xsl:text>
			</xsl:when>
			<xsl:when test="$condition = 22">
				<xsl:text>r</xsl:text>
			</xsl:when>
			<xsl:when test="$condition = 24 or $condition = 31">
				<xsl:text>E</xsl:text>
			</xsl:when>
			<xsl:when test="$condition = 25">
				<xsl:text>u</xsl:text>
			</xsl:when>
			<xsl:when test="$condition = 29">
				<xsl:text>v</xsl:text>
			</xsl:when>
			<xsl:when test="$condition = 30">
				<xsl:text>5</xsl:text>
			</xsl:when>
			<xsl:when test="$condition = 32">
				<xsl:text>6</xsl:text>
			</xsl:when>
			<xsl:when test="$condition = 33">
				<xsl:text>A</xsl:text>
			</xsl:when>
			<xsl:when test="$condition = 34 or $condition = 36 or $condition = 37">
				<xsl:text>B</xsl:text>
			</xsl:when>
			<xsl:when test="$condition = 35 or $condition = 38">
				<xsl:text>C</xsl:text>
			</xsl:when>
			<xsl:when test="$condition = 39 or $condition = 40">
				<xsl:text>G</xsl:text>
			</xsl:when>
			<xsl:when test="$condition = 41 or $condition = 42">
				<xsl:text>K</xsl:text>
			</xsl:when>
			<xsl:when test="$condition = 43 or $condition = 44">
				<xsl:text>O</xsl:text>
			</xsl:when>
			<!-- N/A -->
			<xsl:otherwise>
				<xsl:text>-</xsl:text>
			</xsl:otherwise>
		</xsl:choose>
		<xsl:text> -- </xsl:text>
		<xsl:value-of select="title"/>
		<xsl:if test="position() != 1">
			<xsl:text>: </xsl:text>
			<xsl:value-of select="substring-before(description, '&lt;')"/>
		</xsl:if>
	</xsl:template>
</xsl:stylesheet>
