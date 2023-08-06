<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

<!--
<xsl:import href="/home/pietro/Desktop/docbookproc/projects/liberidalleossessioni/info/info.xsl"/>
-->
<xsl:import href="/Applications/MAMP/htdocs/kepub/projects/liberidalleossessioni/info/info.xsl"/>

<xsl:template match="/">
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="book">
  <xsl:text disable-output-escaping="yes"><![CDATA[<book lang="it" version="5.0" xmlns="http://docbook.org/ns/docbook"
      xmlns:xlink="http://www.w3.org/1999/xlink"
      xmlns:xi="http://www.w3.org/2001/XInclude"
      xmlns:svg="http://www.w3.org/2000/svg"
      xmlns:m="http://www.w3.org/1998/Math/MathML"
      xmlns:html="http://www.w3.org/1999/xhtml"
      xmlns:db="http://docbook.org/ns/docbook">
      ]]></xsl:text>
    <xsl:call-template name="addinfo"/>
    <xsl:apply-templates/>
  <xsl:text disable-output-escaping="yes"><![CDATA[</book>]]></xsl:text>
</xsl:template>

<xsl:template match="book/*">
  <xsl:copy-of select="."/>
</xsl:template>

</xsl:stylesheet>
