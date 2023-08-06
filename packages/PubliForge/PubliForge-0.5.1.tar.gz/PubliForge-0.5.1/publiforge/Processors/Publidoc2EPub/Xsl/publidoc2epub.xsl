<?xml version="1.0" encoding="utf-8"?>
<!-- $Id: publidoc2epub.xsl b1ffa5a75b89 2012/02/19 23:23:01 patrick $ -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:import href="publidoc2html_base.inc.xsl"/>
  <xsl:import href="publidoc2html_cals.inc.xsl"/>
  <xsl:import href="publidoc2html_ini.inc.xsl"/>
  <xsl:import href="publidoc2epub_opf.inc.xsl"/>
  <xsl:import href="publidoc2epub_ncx.inc.xsl"/>
  <xsl:import href="publidoc2epub_base.inc.xsl"/>

  <!-- PubliForge parameters -->
  <xsl:param name="output"/>          <!-- Full path to output directory -->
  <xsl:param name="fid"/>             <!-- XML File name without extension -->

  <!-- Processor image parameters (Publidoc2Html) -->
  <xsl:param name="img" select="1"/>
  <xsl:param name="img_src_file">%(filepath)s/Images/%(id)s.jpg</xsl:param>   
  <xsl:param name="img_src_paths">%(filepath)s</xsl:param>   
  <xsl:param name="img_src_patterns">Images/%(id)s.%(ext)s</xsl:param>   
  <xsl:param name="img_ext">.png</xsl:param>
  <xsl:param name="img_size">420x420&gt;</xsl:param>
  <xsl:param name="img_size_cover">1024x768&gt;</xsl:param>
  <xsl:param name="img_size_thumbnail">160x160&gt;</xsl:param>
  <xsl:param name="img_optimize" select="4"/>
  <!-- Processor audio parameters (Publidoc2Html) -->
  <xsl:param name="aud" select="0"/>
  <xsl:param name="aud_src_file">%(filepath)s/Audios/%(id)s.wav</xsl:param>   
  <xsl:param name="aud_src_paths">%(filepath)s</xsl:param>   
  <xsl:param name="aud_src_patterns">Audios/%(id)s.%(ext)s</xsl:param>   
  <xsl:param name="aud_ext">.ogg</xsl:param>
  <!-- Processor ePub parameters -->
  <xsl:param name="toc" select="0"/>       <!-- With main TOC -->
  <xsl:param name="subtoc" select="0"/>    <!-- With intermediate TOC -->
  <xsl:param name="ean"/>                  <!-- EAN -->
  <xsl:param name="cover"/>                <!-- Cover -->
  <xsl:param name="publisher_label"/>      <!-- Publisher label -->
  <xsl:param name="publisher_url"/>        <!-- Publisher URL -->

  <!-- Variables -->
  <xsl:variable name="path" select="concat($output, 'Container~/OEBPS/')"/>
  <xsl:variable name="img_dir">Images/</xsl:variable>
  <xsl:variable name="aud_dir">Audios/</xsl:variable>


  <xsl:output method="xml" encoding="utf-8" indent="yes"
              doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN"
              doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"/>

  <!--
      =========================================================================
      publiset
      =========================================================================
  -->
  <xsl:template match="publiset"/>
  
  <!--
      =========================================================================
      publidoc
      =========================================================================
  -->
  <xsl:template match="publidoc">
    <xsl:apply-templates select="document|topic"/>
    <xsl:choose>
      <xsl:when test="$cover">
        <xsl:apply-templates select="//image[name(..)!='cover']" mode="ini"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:apply-templates select="//image" mode="ini"/>
      </xsl:otherwise>
    </xsl:choose>
    <xsl:apply-templates select="//audio" mode="ini"/>
  </xsl:template>

  <!--
      =========================================================================
      document
      =========================================================================
  -->
  <xsl:template match="document">
    <xsl:call-template name="cover"/>
    <xsl:if test="$toc"><xsl:call-template name="toc"/></xsl:if>

    <xsl:if test="$subtoc">
      <xsl:apply-templates select="division" mode="file"/>
    </xsl:if>
    <xsl:apply-templates select=".//topic" mode="file"/>

    <xsl:call-template name="content_opf"/>
    <xsl:call-template name="toc_ncx"/>
  </xsl:template>

  <!--
      =========================================================================
      topic
      =========================================================================
  -->
  <xsl:template match="topic">
    <xsl:call-template name="cover"/>
    <xsl:if test="$toc"><xsl:call-template name="toc"/></xsl:if>

    <xsl:call-template name="html_file">
      <xsl:with-param name="name" select="concat($fid, '-tpc-1')"/>
      <xsl:with-param name="title">
        <xsl:value-of select="head/title"/>
      </xsl:with-param>
      <xsl:with-param name="body">
        <body>
          <xsl:attribute name="class">
            <xsl:text>pdocTopic</xsl:text>
            <xsl:if test="@type"> pdocTopic-<xsl:value-of select="@type"/></xsl:if>
          </xsl:attribute>
          <div><a id="top"><xsl:text> </xsl:text></a></div>
          <xsl:if test="head/title">
            <div class="h1"><xsl:apply-templates select="head/title"/></div>
          </xsl:if>
          <xsl:if test="head/subtitle">
            <div class="h2"><xsl:apply-templates select="head/subtitle"/></div>
          </xsl:if>
          <xsl:apply-templates select="." mode="corpus"/>
        </body>
      </xsl:with-param>
    </xsl:call-template>

    <xsl:call-template name="content_opf"/>
    <xsl:call-template name="toc_ncx"/>
  </xsl:template>

</xsl:stylesheet>
