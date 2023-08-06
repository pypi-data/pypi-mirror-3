<?xml version="1.0" encoding="UTF-8" ?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

<!-- odt2docbook7.xsl version 1.4 -->

<xsl:template match="/">
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="book">
  <xsl:text disable-output-escaping="yes"><![CDATA[<book xml:lang="it" version="5.0" xmlns="http://docbook.org/ns/docbook"
      xmlns:xlink="http://www.w3.org/1999/xlink"
      xmlns:xi="http://www.w3.org/2001/XInclude"
      xmlns:svg="http://www.w3.org/2000/svg"
      xmlns:m="http://www.w3.org/1998/Math/MathML"
      xmlns:html="http://www.w3.org/1999/xhtml"
      xmlns:db="http://docbook.org/ns/docbook">
      ]]></xsl:text>

  <xsl:apply-templates/>
  <xsl:text disable-output-escaping="yes"><![CDATA[</book>]]></xsl:text>
</xsl:template>

<xsl:template match="node()|@*"> 
  <xsl:copy>
    <xsl:apply-templates/>
  </xsl:copy>
</xsl:template>

<xsl:template match="chapter">
  <xsl:copy-of select="."/>
</xsl:template>

<xsl:template match="section">
  <xsl:copy-of select="."/>
</xsl:template>

<xsl:template match="sidebar">
  <xsl:copy-of select="."/>
</xsl:template>

<xsl:template match="bridgehead">
  <xsl:copy-of select="."/>
</xsl:template>

<xsl:template match="title">
  <xsl:copy-of select="."/>
</xsl:template>

<xsl:template match="para">
  <xsl:copy-of select="."/>
</xsl:template>

<xsl:template match="emphasis">
  <xsl:copy-of select="."/>
</xsl:template>

<xsl:template match="para">
  <xsl:copy-of select="."/>
</xsl:template>

<xsl:template match="imagedata">
  <xsl:copy-of select="."/>
</xsl:template>

<xsl:template match="table">
  <xsl:copy-of select="."/>
</xsl:template> 

</xsl:stylesheet>
