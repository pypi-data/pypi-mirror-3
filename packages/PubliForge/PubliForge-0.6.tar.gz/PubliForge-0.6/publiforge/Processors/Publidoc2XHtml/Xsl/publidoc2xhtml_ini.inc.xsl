<?xml version='1.0' encoding="utf-8"?>
<!-- $Id: publidoc2xhtml_ini.inc.xsl 3bc6007adb6e 2012/06/01 08:00:35 claire $ -->
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
      * %(filepath)s = full path to the processed file directory
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
      image mode ini & template image_ini
      =========================================================================
  -->
  <xsl:template match="image" mode="ini">
    <xsl:if test="$img">
      <xsl:call-template name="image_ini">
        <xsl:with-param name="size">
          <xsl:choose>
            <xsl:when test="ancestor::cover">
              <xsl:value-of select="$img_size_cover"/>
            </xsl:when>
            <xsl:when test="@type='thumbnail'">
              <xsl:value-of select="$img_size_thumbnail"/>
            </xsl:when>
            <xsl:when test="@type='icon' or not(ancestor::media)">
              <xsl:value-of select="$img_size_icon"/>
            </xsl:when>
            <xsl:otherwise><xsl:value-of select="$img_size"/></xsl:otherwise>
          </xsl:choose>
        </xsl:with-param>
        <xsl:with-param name="ext">
          <xsl:choose>
            <xsl:when test="ancestor::tooltip">.png</xsl:when>
            <xsl:otherwise><xsl:value-of select="$img_ext"/></xsl:otherwise>
          </xsl:choose>
        </xsl:with-param>
      </xsl:call-template>
    </xsl:if>
  </xsl:template>

  <xsl:template name="image_ini">
    <xsl:param name="size"/>
    <xsl:param name="ext"><xsl:value-of select="$img_ext"/></xsl:param>
    <xsl:document href="{$path}{$fid}-img{count(preceding::image)+1}-{count(ancestor::image)}~.ini"
                  method="text" encoding="utf-8">
[Source]
type = image
id = <xsl:value-of select="@id"/>
search = <xsl:value-of select="$img_search"/>

[Target]
file = %(here)s/<xsl:value-of select="concat($img_dir, @id, $ext)"/>

[Transformation]
<xsl:choose>
<xsl:when test="$ext='.png'">
step.1 = nice convert -strip -colorspace RGB %(source)s -quality 100
         -geometry <xsl:value-of select="$size"/> %(target)s
<xsl:if test="$img_optimize">
step.2 = nice optipng -o<xsl:value-of select="$img_optimize"/> %(target)s
step.3 = nice advpng -z -q -4 %(target)s
</xsl:if>
</xsl:when>
<xsl:when test="$ext='.jpg' or $ext='.jpeg'">
step.1 = nice convert -strip -colorspace RGB %(source)s
         -quality <xsl:value-of select="$img_quality"/>
         -geometry <xsl:value-of select="$size"/> %(target)s
<xsl:if test="$img_optimize">
step.2 = nice jpegoptim -q %(target)s
</xsl:if>
</xsl:when>
<xsl:otherwise>
step.1 = nice convert -strip -colorspace RGB %(source)s
         -geometry <xsl:value-of select="$size"/> %(target)s
</xsl:otherwise>
</xsl:choose>

[Transformation:eps]
step.1 = nice convert -strip -colorspace RGB %(source)s -density 300x300
         -geometry <xsl:value-of select="$size"/> %(target)s
<xsl:if test="$ext='.png' and $img_optimize">
step.2 = nice optipng -o<xsl:value-of select="$img_optimize"/> %(target)s
step.3 = nice advpng -z -q -4 %(target)s
</xsl:if>
<xsl:if test="$ext='.jpg' and $img_optimize">
step.2 = nice jpegoptim -q %(target)s
</xsl:if>
    </xsl:document>
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
search = <xsl:value-of select="$aud_search"/>

[Target]
file = %(here)s/<xsl:value-of select="concat($aud_dir, @id, $aud_ext)"/>

[Transformation]
<xsl:choose>
  <xsl:when test="$aud_ext='.ogg'">
step.1 = nice ffmpeg -i %(source)s -acodec libvorbis -ab 128k -y %(target)s
  </xsl:when>
  <xsl:when test="$aud_ext='.aac'">
step.1 = nice ffmpeg -i %(source)s -strict experimental -ab 128k -y %(target)s
  </xsl:when>
  <xsl:otherwise>
step.1 = nice ffmpeg -i %(source)s -ab 128k -y %(target)s
  </xsl:otherwise>
</xsl:choose>
      </xsl:document>
    </xsl:if>
  </xsl:template>

</xsl:stylesheet>
