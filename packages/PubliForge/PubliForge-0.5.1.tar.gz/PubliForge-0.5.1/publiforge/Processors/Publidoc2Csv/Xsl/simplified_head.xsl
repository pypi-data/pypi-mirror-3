<?xml version="1.0" encoding="utf-8"?>
<!-- $Id: simplified_head.xsl 816eec7f0a0c 2012/03/22 10:22:19 patrick $ -->
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
      head
      =========================================================================
  -->
  <xsl:template match="head/date"/>
  <xsl:template match="head/place"/>
  <xsl:template match="head/source"/>
  <xsl:template match="head/subjectset"/>
  <xsl:template match="head/keywordset"/>

</xsl:stylesheet>
