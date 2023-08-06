<?xml version='1.0' encoding="utf-8"?>
<!-- $Id: publidoc2epub3_base.inc.xsl c2bf037d7acc 2012/05/01 20:30:09 patrick $ -->
<xsl:stylesheet version="1.1" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <!--
      *************************************************************************
                                  CALLABLE TEMPLATES
      *************************************************************************
  -->
  <!--
      =========================================================================
      Template html_file
      =========================================================================
  -->
  <xsl:template name="html_file">
    <xsl:param name="name"/>
    <xsl:param name="title"/>
    <xsl:param name="body"/>
    <xsl:document href="{$path}{$name}{$html_ext}" method="xml"
                  encoding="utf-8" indent="yes">
      <xsl:call-template name="html_frame">
        <xsl:with-param name="title" select="$title"/>
        <xsl:with-param name="body" select="$body"/>
      </xsl:call-template>
    </xsl:document>
  </xsl:template>

</xsl:stylesheet>
