<?xml version='1.0' encoding="utf-8"?>
<!-- $Id: publidoc2html5_ini.inc.xsl ef87ae8aab5a 2012/08/31 16:51:06 patrick $ -->
<xsl:stylesheet version="1.1" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <!--
      =========================================================================
      This XSL creates INI files for LePrisme engine.

      Cf. publidoc2xhtml_ini.inc.xsl
      =========================================================================
  -->

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
file = %(here)s/<xsl:value-of select="concat($aud_dir, @id, $aud_ext1)"/>

[Transformation]
<xsl:choose>
  <xsl:when test="$aud_ext1='.ogg'">
step.1 = nice ffmpeg -i "%(source)s" -acodec libvorbis -ab 128k -y "%(target)s"
  </xsl:when>
  <xsl:when test="$aud_ext1='.aac' or $aud_ext1='.m4a'">
step.1 = nice ffmpeg -i "%(source)s" -strict experimental -ab 128k -y "%(target)s"
  </xsl:when>
  <xsl:otherwise>
step.1 = nice ffmpeg -i "%(source)s" -ab 128k -y "%(target)s"
  </xsl:otherwise>
</xsl:choose>

<xsl:if test="$aud_ext1!=$aud_ext2">
  <xsl:choose>
    <xsl:when test="$aud_ext2='.ogg'">
step.2 = nice ffmpeg -i "%(source)s" -acodec libvorbis -ab 128k
         -y "%(here)s/<xsl:value-of select="concat($aud_dir, @id, $aud_ext2)"/>"
    </xsl:when>
    <xsl:when test="$aud_ext2='.aac' or $aud_ext2='.m4a'">
step.2 = nice ffmpeg -i "%(source)s" -strict experimental -ab 128k
         -y "%(here)s/<xsl:value-of select="concat($aud_dir, @id, $aud_ext2)"/>"
    </xsl:when>
    <xsl:otherwise>
step.2 = nice ffmpeg -i "%(source)s" -ab 128k
         -y "%(here)s/<xsl:value-of select="concat($aud_dir, @id, $aud_ext2)"/>"
    </xsl:otherwise>
  </xsl:choose>
</xsl:if>
      </xsl:document>
    </xsl:if>
  </xsl:template>

</xsl:stylesheet>
