<?xml version='1.0' encoding="utf-8"?>
<!-- $Id: publidoc2html_ini.inc.xsl b1ffa5a75b89 2012/02/19 23:23:01 patrick $ -->
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
    <xsl:variable name="size">
      <xsl:choose>
        <xsl:when test="@type='cover' or ancestor::cover">
          <xsl:value-of select="$img_size_cover"/>
        </xsl:when>
        <xsl:when test="@type='thumbnail'">
          <xsl:value-of select="$img_size_thumbnail"/>
        </xsl:when>
        <xsl:otherwise><xsl:value-of select="$img_size"/></xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="$img">
      <xsl:document href="{$path}{$fid}-img{count(preceding::image)+1}~.ini"
                    method="text" encoding="utf-8">
[Source]
type = image
id = <xsl:value-of select="@id"/>
file = <xsl:value-of select="$img_src_file"/>
paths = <xsl:value-of select="$img_src_paths"/>
patterns = <xsl:value-of select="$img_src_patterns"/>

[Target]
file = %(here)s/<xsl:value-of select="concat($img_dir, @id, $img_ext)"/>

[Transformation]
step.1 = nice convert -colorspace RGB %(source)s
         -geometry <xsl:value-of select="$size"/> %(target)s
<xsl:if test="$img_ext='.png' and $img_optimize">         
step.2 = nice optipng -o<xsl:value-of select="$img_optimize"/> %(target)s
step.3 = nice advpng -z -q -4 %(target)s
</xsl:if>
<xsl:if test="$img_ext='.jpg' and $img_optimize">         
step.2 = nice jpegoptim -q %(target)s
</xsl:if>

[Transformation:eps]
step.1 = nice convert -density 200x200 -colorspace RGB %(source)s
         -geometry <xsl:value-of select="$size"/> %(target)s
<xsl:if test="$img_ext='.png' and $img_optimize">         
step.2 = nice optipng -o<xsl:value-of select="$img_optimize"/> %(target)s
step.3 = nice advpng -z -q -4 %(target)s
</xsl:if>
<xsl:if test="$img_ext='.jpg' and $img_optimize">         
step.2 = nice jpegoptim -q %(target)s
</xsl:if>
      </xsl:document>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      audio mode ini
      =========================================================================
  -->
  <xsl:template match="audio" mode="ini">
    <xsl:if test="$aud">
      <xsl:document href="{$path}{$fid}-aud{count(preceding::audio)+1}~.ini"
                    method="text" encoding="utf-8">
[Source]
type = audio
id = <xsl:value-of select="@id"/>
file = <xsl:value-of select="$aud_src_file"/>
paths = <xsl:value-of select="$aud_src_paths"/>
patterns = <xsl:value-of select="$aud_src_patterns"/>

[Target]
file = %(here)s/<xsl:value-of select="concat($aud_dir, @id, $aud_ext)"/>

[Transformation]
step.1 = nice ffmpeg -i %(source)s -y %(target)s
      </xsl:document>
    </xsl:if>
  </xsl:template>

</xsl:stylesheet>
