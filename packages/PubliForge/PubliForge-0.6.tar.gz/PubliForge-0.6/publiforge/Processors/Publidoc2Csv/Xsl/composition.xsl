<?xml version="1.0" encoding="utf-8"?>
<!-- $Id: composition.xsl fb4fb99eed62 2012/04/29 18:57:00 patrick $ -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml" encoding="utf-8" indent="yes"/>

  <!--
      =========================================================================
      Copy
      =========================================================================
  -->
  <xsl:template match="*|@*|text()">
    <xsl:copy>
      <xsl:apply-templates select="*|@*|text()|processing-instruction()"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="processing-instruction()">
    <xsl:copy/><xsl:text>
</xsl:text>
  </xsl:template>

  <!--
      =========================================================================
      publidoc
      =========================================================================
  -->
  <xsl:template match="publidoc">
    <xsl:apply-templates/>
  </xsl:template>

  <!--
      =========================================================================
      head
      =========================================================================
  -->
  <xsl:template match="head">
    <head>
      <xsl:apply-templates select="title"/>
    </head>
  </xsl:template>

</xsl:stylesheet>
