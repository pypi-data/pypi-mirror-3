<?xml version='1.0' encoding="utf-8"?>
<!-- $Id: publiquiz2html_ini.inc.xsl 1f6e485627e4 2012/03/09 11:22:06 patrick $ -->
<xsl:stylesheet version="1.1" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <!--
      =========================================================================
      This XSL creates INI files for LePrisme engine.

      Sections are:

      * [Source]
      * [Target]
      * [Transformation]
      * [Transformation:<source_extension>]

      Special strings are:

      * %(stgpath)s = full path to the storage root directory
      * %(filepath)s = full path to the original file
      * %(output)s = full path to the output directory
      * %(here)s = full path to INI file
      * %(id)s = source ID
      * %(ext)s = one of possible extensions for the source file
      * %(source)s = source file
      * %(target)s = target file
      =========================================================================
  -->

  <!--
      =========================================================================
      image mode ini
      =========================================================================
  -->
  <xsl:template match="image" mode="ini">
    <xsl:if test="$img">
      <xsl:call-template name="image_ini">
        <xsl:with-param name="size">
          <xsl:choose>
            <xsl:when test="@type='cover' or ancestor::cover">
              <xsl:value-of select="$img_size_cover"/>
            </xsl:when>
            <xsl:when test="@type='thumbnail' or ancestor::match">
              <xsl:value-of select="$img_size_thumbnail"/>
            </xsl:when>
            <xsl:otherwise><xsl:value-of select="$img_size"/></xsl:otherwise>
          </xsl:choose>
        </xsl:with-param>
      </xsl:call-template>
    </xsl:if>
  </xsl:template>

</xsl:stylesheet>
