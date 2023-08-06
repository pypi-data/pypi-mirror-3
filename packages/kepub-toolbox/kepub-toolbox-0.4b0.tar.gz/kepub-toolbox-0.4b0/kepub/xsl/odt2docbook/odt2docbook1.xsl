<?xml version="1.0" encoding="UTF-8" ?>

<xsl:stylesheet
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0" exclude-result-prefixes="text office draw xlink table svg">

  <!-- odt2docbook1.xsl version 2.3 -->

  <xsl:template match="/">
    <book>
      <xsl:apply-templates/>
    </book>
  </xsl:template>

  <xsl:template match="text:h[@text:outline-level='1']">
    <chapter>
      <xsl:apply-templates/>
    </chapter>
  </xsl:template>


  <xsl:template match="text:h[@text:outline-level='2']">
    <header1>
      <xsl:apply-templates/>
    </header1>
  </xsl:template>

  <xsl:template match="text:h[@text:outline-level='3']">
    <header2>
      <xsl:apply-templates/>
    </header2>
  </xsl:template>

  <xsl:template match="text:h[@text:outline-level='4']">
    <header3>
      <xsl:apply-templates/>
    </header3>
  </xsl:template>

  <xsl:template match="text:h[@text:outline-level='5']">
    <header4>
      <xsl:apply-templates/>
    </header4>
  </xsl:template>

  <xsl:template match="text:p[@text:style-name='Heading']">
    <para role="generic-header"><xsl:value-of select="."/></para>
  </xsl:template>

  <xsl:template match="text:p[@text:style-name='Text_20_body']">
    <xsl:choose>
      <xsl:when test="draw:frame/svg:title/text()='box'">
	<sidebar role="box"><xsl:apply-templates/></sidebar>
      </xsl:when>
      <xsl:when test="draw:frame/svg:title/text()='avvertenza'">
	<sidebar role="avvertenza"><xsl:apply-templates/></sidebar>
      </xsl:when>
      <xsl:when test="draw:frame/svg:title/text()='faq'">
	<sidebar role="faq"><xsl:apply-templates/></sidebar>
      </xsl:when>
      <xsl:when test="draw:frame/svg:title/text()='blockquote'">
	<blockquote><xsl:apply-templates/></blockquote>
      </xsl:when>
      <xsl:when test="draw:frame/draw:text-box/text:p[@text:style-name='Illustration']">
	<mediaobject>
	  <xsl:apply-templates select="draw:frame/draw:text-box/text:p[@text:style-name='Illustration']"/>
	</mediaobject>
      </xsl:when>
      <xsl:otherwise>
	<para><xsl:apply-templates/></para>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="text:p[@text:style-name='Illustration']">
    <imageobject>
      <xsl:apply-templates select="draw:frame/draw:image"/>
    </imageobject>
    <caption><para><xsl:value-of select="."/></para></caption>
  </xsl:template>

  <xsl:template match="svg:title">
    <xsl:text></xsl:text>
  </xsl:template>

  <xsl:template match="svg:description">
    <xsl:text></xsl:text>
  </xsl:template>

  <xsl:template match="text:list">
    <itemizedlist>
      <xsl:apply-templates/>
    </itemizedlist>
  </xsl:template>

  <xsl:template match="text:list/text:list-item">
    <listitem>
      <para><xsl:value-of select="."/></para>
    </listitem>
  </xsl:template>

  <xsl:template match="draw:image">
    <imagedata fileref="{@xlink:href}"/>
  </xsl:template>  

  <xsl:template match="table:table">
    <table>
      <caption></caption>
      <thead>
	<xsl:apply-templates select="table:table-row[position()=1]"/>
      </thead>
      <tbody>
	<xsl:apply-templates select="table:table-row[not(position()=1)]"/>
      </tbody>
    </table>    
  </xsl:template>

  <xsl:template match="table:table/table:table-row[position()=1]">
      <tr>
	<xsl:for-each select="table:table-cell">
	  <td><xsl:apply-templates/></td>
	</xsl:for-each>
      </tr>
  </xsl:template>

  <xsl:template match="table:table/table:table-row[not(position()=1)]">
      <tr>
	<xsl:for-each select="table:table-cell">
	  <td><xsl:apply-templates/></td>
	</xsl:for-each>
      </tr>
  </xsl:template>

  <xsl:template match="table:table-cell/text:p">
      <xsl:value-of select="."/>
  </xsl:template>

  <xsl:template match="text:span">
      <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="text:span[@text:style-name='T1']">
    <emphasis role="italic"><xsl:value-of select="."/></emphasis>
  </xsl:template>

  <xsl:template match="text:span[@text:style-name='T2']">
    <emphasis role="bold"><xsl:value-of select="."/></emphasis>
  </xsl:template>

  <xsl:template match="text:p[@text:style-name='P1']">
    <para role="italic"><xsl:value-of select="."/></para>
  </xsl:template>


  

</xsl:stylesheet>

