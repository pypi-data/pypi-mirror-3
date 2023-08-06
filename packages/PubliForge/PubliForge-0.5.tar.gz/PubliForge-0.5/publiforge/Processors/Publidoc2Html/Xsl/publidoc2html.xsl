<?xml version="1.0" encoding="utf-8"?>
<!-- $Id: publidoc2html.xsl ad37032b83b9 2011/11/23 00:11:03 patrick $ -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:import href="publidoc2html_base.inc.xsl"/>
  <xsl:import href="publidoc2html_cals.inc.xsl"/>
  <xsl:import href="publidoc2html_ini.inc.xsl"/>

  <!-- PubliForge parameters -->
  <xsl:param name="output"/>   <!-- Full path to output directory -->
  <xsl:param name="fid"/>      <!-- XML File name without extension -->

  <!-- Processor image parameters -->
  <xsl:param name="img" select="1"/>
  <xsl:param name="img_src_file">%(filepath)s/Images/%(id)s.jpg</xsl:param>   
  <xsl:param name="img_src_paths">%(filepath)s</xsl:param>   
  <xsl:param name="img_src_patterns">Images/%(id)s.%(ext)s</xsl:param>   
  <xsl:param name="img_ext">.png</xsl:param>
  <xsl:param name="img_size">420x420&gt;</xsl:param>
  <xsl:param name="img_size_cover">420x640&gt;</xsl:param>
  <xsl:param name="img_size_thumbnail">160x160&gt;</xsl:param>
  <xsl:param name="img_optimize" select="4"/>
  <!-- Processor audio parameters -->
  <xsl:param name="aud" select="0"/>
  <xsl:param name="aud_src_file">%(filepath)s/Audios/%(id)s.wav</xsl:param>   
  <xsl:param name="aud_src_paths">%(filepath)s</xsl:param>   
  <xsl:param name="aud_src_patterns">Audios/%(id)s.%(ext)s</xsl:param>   
  <xsl:param name="aud_ext">.ogg</xsl:param>
  <!-- Processor HTML parameters -->
  <xsl:param name="onefile" select="0"/>  <!-- all in one HTML file -->
  <xsl:param name="subtoc" select="0"/>   <!-- with intermediate TOC -->

  <!-- Variables -->
  <xsl:variable name="path" select="$output"/>
  <xsl:variable name="img_dir">Images/</xsl:variable>
  <xsl:variable name="aud_dir">Audios/</xsl:variable>

  <xsl:output method="xml" encoding="utf-8" indent="yes"
              doctype-public="-//W3C//DTD XHTML 1.1//EN"
              doctype-system="http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd"/>

  <!--
      =========================================================================
      publiset
      =========================================================================
  -->
  <xsl:template match="publiset">
    <xsl:apply-templates select="selection"/>
  </xsl:template>

  <!--
      =========================================================================
      publidoc
      =========================================================================
  -->
  <xsl:template match="publidoc">
    <xsl:apply-templates select="document|topic"/>
    <xsl:apply-templates select="//image" mode="ini"/>
    <xsl:apply-templates select="//audio" mode="ini"/>
  </xsl:template>

  <!--
      =========================================================================
      selection
      =========================================================================
  -->
  <xsl:template match="selection">
    <xsl:call-template name="html_frame">
      <xsl:with-param name="title">
        <xsl:value-of select="head/title"/>
      </xsl:with-param>
      <xsl:with-param name="body">
        <body class="pdocToc">
          <xsl:if test="head/title">
            <h1><xsl:apply-templates select="head/title"/></h1>
          </xsl:if>
          <xsl:if test="head/subtitle">
            <h2><xsl:apply-templates select="head/subtitle"/></h2>
          </xsl:if>
          <ul>
            <xsl:apply-templates select="division|file|link" mode="toc"/>
          </ul>
        </body>
      </xsl:with-param>
    </xsl:call-template>
  </xsl:template>

  <!--
      =========================================================================
      document
      =========================================================================
  -->
  <xsl:template match="document">
    <xsl:call-template name="html_frame">
      <xsl:with-param name="title">
        <xsl:value-of select="head/title"/>
      </xsl:with-param>
      <xsl:with-param name="body">
        <body>
          <xsl:choose>
            <!-- ~~~~~~~~~~~~~~~~~~~~~~~~~ One file ~~~~~~~~~~~~~~~~~~~~~~~ -->
            <xsl:when test="$onefile=1">
              <xsl:attribute name="class">pdocDoc</xsl:attribute>
              <xsl:if test="head/title">
                <h1><xsl:apply-templates select="head/title"/></h1>
              </xsl:if>
              <xsl:if test="head/subtitle">
                <h2><xsl:apply-templates select="head/subtitle"/></h2>
              </xsl:if>
              <xsl:apply-templates select="division|topic" mode="onefile"/>
            </xsl:when>
            
            <!-- ~~~~~~~~~~~~~~~~~~~~~~~~ Multi files ~~~~~~~~~~~~~~~~~~~~~ -->
            <xsl:otherwise>
              <xsl:attribute name="class">pdocToc</xsl:attribute>
              <xsl:if test="head/title">
                <h1><xsl:apply-templates select="head/title"/></h1>
              </xsl:if>
              <xsl:if test="head/subtitle">
                <h2><xsl:apply-templates select="head/subtitle"/></h2>
              </xsl:if>
              <ul>
                <xsl:choose>
                  <xsl:when test="$subtoc and division">
                    <xsl:apply-templates select="division|topic" mode="maintoc"/>
                    <xsl:apply-templates select="division" mode="file"/>
                  </xsl:when>
                  <xsl:otherwise>
                    <xsl:apply-templates select="division|topic" mode="toc"/>
                  </xsl:otherwise>
                </xsl:choose>
              </ul>
              <xsl:apply-templates select=".//topic" mode="file"/>
            </xsl:otherwise>
          </xsl:choose>
        </body>
      </xsl:with-param>
    </xsl:call-template>
  </xsl:template>

  <!--
      =========================================================================
      topic
      =========================================================================
  -->
  <xsl:template match="topic">
    <xsl:call-template name="html_frame">
      <xsl:with-param name="title">
        <xsl:value-of select="head/title"/>
      </xsl:with-param>
      <xsl:with-param name="body">
        <body>
          <xsl:attribute name="class">
            <xsl:text>pdocTopic</xsl:text>
            <xsl:if test="@type"> pdocTopic-<xsl:value-of select="@type"/></xsl:if>
          </xsl:attribute>
          <xsl:if test="head/title">
            <h1><xsl:apply-templates select="head/title"/></h1>
          </xsl:if>
          <xsl:if test="head/subtitle">
            <h2><xsl:apply-templates select="head/subtitle"/></h2>
          </xsl:if>
          <xsl:apply-templates select="." mode="corpus"/>
        </body>
      </xsl:with-param>
    </xsl:call-template>
  </xsl:template>

</xsl:stylesheet>
