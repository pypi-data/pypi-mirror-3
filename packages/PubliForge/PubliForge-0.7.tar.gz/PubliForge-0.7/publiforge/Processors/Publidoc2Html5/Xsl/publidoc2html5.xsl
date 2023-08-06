<?xml version="1.0" encoding="utf-8"?>
<!-- $Id: publidoc2html5.xsl baa87d7878d9 2012/08/01 13:54:45 patrick $ -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:import href="publidoc2xhtml.xsl"/>
  <xsl:import href="publidoc2html5_base.inc.xsl"/>
  <xsl:import href="publidoc2html5_ini.inc.xsl"/>

  <!-- PubliForge parameters -->
  <xsl:param name="processor"/>   <!-- Full path to processor directory -->
  <xsl:param name="output"/>      <!-- Full path to output directory -->
  <xsl:param name="fid"/>         <!-- XML File name without extension -->

  <!-- Processor image parameters -->
  <xsl:param name="img" select="1"/>
  <xsl:param name="img_search">%(id)s.%(ext)s</xsl:param>
  <xsl:param name="img_quality" select="92"/>
  <xsl:param name="img_optimize" select="4"/>
  <xsl:param name="img_ext">.png</xsl:param>
  <xsl:param name="img_size">640x480&gt;</xsl:param>
  <xsl:param name="img_size_thumbnail">160x160&gt;</xsl:param>
  <xsl:param name="img_size_icon">x32&gt;</xsl:param>
  <xsl:param name="img_size_cover">768x1024&gt;</xsl:param>
  <!-- Processor audio parameters -->
  <xsl:param name="aud" select="1"/>
  <xsl:param name="aud_search">%(id)s.%(ext)s</xsl:param>
  <xsl:param name="aud_ext1">.ogg</xsl:param>
  <xsl:param name="aud_ext2">.aac</xsl:param>
  <!-- Processor video parameters -->
  <xsl:param name="vid" select="1"/>
  <xsl:param name="vid_search">%(id)s.%(ext)s</xsl:param>
  <xsl:param name="vid_ext">.ogv</xsl:param>
  <xsl:param name="vid_width">300</xsl:param>
  <!-- Processor HTML 5 parameters -->
  <xsl:param name="onefile" select="0"/>
  <xsl:param name="subtoc" select="0"/>
  <xsl:param name="js" select="0"/>

  <!-- Variables -->
  <xsl:variable name="path" select="$output"/>
  <xsl:variable name="img_dir">Images/</xsl:variable>
  <xsl:variable name="aud_dir">Audios/</xsl:variable>
  <xsl:variable name="vid_dir">Videos/</xsl:variable>
  <xsl:variable name="html_ext">.html</xsl:variable>
  <xsl:variable name="lang">
    <xsl:choose>
      <xsl:when test="/*/*/@xml:lang">
        <xsl:value-of select="/*/*/@xml:lang"/>
      </xsl:when>
      <xsl:otherwise>en</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>


  <xsl:output method="xml" encoding="utf-8" indent="yes"
              omit-xml-declaration="yes"
              doctype-public="" doctype-system="about:legacy-compat"/>
  
</xsl:stylesheet>
