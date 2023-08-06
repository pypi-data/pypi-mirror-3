<?xml version="1.0" encoding="UTF-8" ?>
<xsl:stylesheet
   xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

<!-- odt2docbook2.xsl version 2.2 -->

<xsl:template match="/">
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="book">
  <xsl:copy>
    <xsl:apply-templates/>
    <xsl:text disable-output-escaping="yes"><![CDATA[</chapter>]]></xsl:text>
  </xsl:copy>
</xsl:template>

<xsl:template match="*">
  <xsl:copy>
    <xsl:apply-templates/>
  </xsl:copy>
</xsl:template>

<xsl:template match="chapter[position()=1]">
  <xsl:text disable-output-escaping="yes"><![CDATA[<chapter>]]></xsl:text>
  <title>
    <xsl:value-of select="."/>
  </title>
</xsl:template>

<xsl:template match="chapter">
  <xsl:text disable-output-escaping="yes"><![CDATA[</chapter><chapter>]]></xsl:text>
  <title>
    <xsl:value-of select="."/>
  </title>
</xsl:template>

<xsl:template match="para">
  <xsl:copy-of select="."/>
</xsl:template>

<xsl:template match="header1">
  <xsl:copy-of select="."/>
</xsl:template>

<xsl:template match="header2">
  <xsl:copy-of select="."/>
</xsl:template>

<xsl:template match="header3">
  <xsl:copy-of select="."/>
</xsl:template>

<xsl:template match="header4">
  <xsl:copy-of select="."/>
</xsl:template>

<xsl:template match="sidebar">
  <xsl:copy-of select="."/>
</xsl:template>

<xsl:template match="bridgehead">
  <xsl:copy-of select="."/>
</xsl:template>

<xsl:template match="emphasis">
  <xsl:copy-of select="."/>
</xsl:template>

<xsl:template match="imagedata">
  <xsl:copy-of select="."/>
</xsl:template>

<xsl:template match="table">
  <xsl:copy-of select="."/>
</xsl:template>

<xsl:template match="blockquote">
  <blockquote>
    <attribution><xsl:value-of select="para[last()]"/></attribution>    
    <para><xsl:value-of select="para" /></para>    
  </blockquote>
</xsl:template>

</xsl:stylesheet>

