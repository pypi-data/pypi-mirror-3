<?xml version="1.0" encoding="UTF-8" ?>
<xsl:stylesheet
   xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

<!-- odt2docbook6.xsl version 2.2 -->

<xsl:template match="/">
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="*">
  <xsl:copy>
    <xsl:apply-templates/>
  </xsl:copy>
</xsl:template>

<xsl:template match="chapter/section/section/section">
  <xsl:copy>
    <xsl:apply-templates/>
    <xsl:if test="header4">
      <xsl:text disable-output-escaping="yes"><![CDATA[</section>]]></xsl:text>      
    </xsl:if>
  </xsl:copy>
</xsl:template>

<xsl:template match="section/section/section/header4[position()=1]">
  <xsl:text disable-output-escaping="yes"><![CDATA[<section>]]></xsl:text>
  <title>
    <xsl:value-of select="."/>
  </title>
</xsl:template>

<xsl:template match="section/section/header4[not(position()=1)]">
  <xsl:text disable-output-escaping="yes"><![CDATA[</section><section>]]></xsl:text>
  <title>
    <xsl:value-of select="."/>
  </title>
</xsl:template>

<xsl:template match="chapter">
  <chapter role="{position()}">
    <xsl:apply-templates/>
  </chapter>
</xsl:template>

<xsl:template match="sidebar">
  <sidebar role="{@role}">
    <xsl:apply-templates/>
  </sidebar>
</xsl:template>

<xsl:template match="bridgehead">
  <bridgehead role="{@role}">
    <xsl:apply-templates/>
  </bridgehead>
</xsl:template>

<xsl:template match="title">
  <title role="{@role}">
    <xsl:apply-templates/>
  </title>
</xsl:template>

<xsl:template match="para">
  <xsl:copy-of select="."/>
</xsl:template>

<xsl:template match="emphasis">
  <emphasis role="{@role}">
    <xsl:apply-templates/>
  </emphasis>
</xsl:template>

<xsl:template match="imagedata">
  <xsl:copy-of select="."/>
</xsl:template>

<xsl:template match="table">
  <xsl:text disable-output-escaping="yes"><![CDATA[<table role="]]></xsl:text>
  <xsl:value-of select="count(tbody/tr)+1"/>
  <xsl:text disable-output-escaping="yes"><![CDATA[" annotations="]]></xsl:text>
  <xsl:value-of select="count(thead/tr/td)"/>
  <xsl:text disable-output-escaping="yes"><![CDATA[">]]></xsl:text>
  <xsl:apply-templates/>
  <xsl:text disable-output-escaping="yes"><![CDATA[</table>]]></xsl:text>
</xsl:template>

</xsl:stylesheet>


