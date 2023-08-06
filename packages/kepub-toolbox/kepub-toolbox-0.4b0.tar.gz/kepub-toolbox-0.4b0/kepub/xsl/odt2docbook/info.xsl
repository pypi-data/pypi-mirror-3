<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
   xmlns:d="http://docbook.org/ns/docbook"
   xmlns:xlink="http://www.w3.org/1999/xlink"
   xmlns:xi="http://www.w3.org/2001/XInclude"
   xmlns:svg="http://www.w3.org/2000/svg"
   xmlns:m="http://www.w3.org/1998/Math/MathML"
   xmlns:html="http://www.w3.org/1999/xhtml"
   xmlns:db="http://docbook.org/ns/docbook"
   exclude-result-prefixes="d xlink db xi svg m html"
   version="1.0">

<xsl:template name="addinfo">
<xsl:text disable-output-escaping="yes">
<![CDATA[
<info>
<title>lkj</title>
<subtitle>lkjl</subtitle>
<author>
<personname>lkjl</personname>
</author>
<copyright>
<year>lkjl</year>
<holder>lkjl</holder>
</copyright>
<biblioid class="isbn">lkjl</biblioid>
<publisher>
<publishername>lkjl</publishername>
<address>lkjl</address>
</publisher>
<edition>lkjl</edition>
<legalnotice>
<para>lkjl</para>
</legalnotice>
</info>]]>
</xsl:text>
</xsl:template>

<xsl:template match="/">
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="d:book">
  <xsl:copy>
    <xsl:for-each select="@*">
      <xsl:copy/>
    </xsl:for-each>
    <xsl:call-template name="addinfo"/>
    <xsl:apply-templates/>
  </xsl:copy>
</xsl:template>

<xsl:template match="d:book/*">
  <xsl:copy-of select="."/>
</xsl:template>

</xsl:stylesheet>
