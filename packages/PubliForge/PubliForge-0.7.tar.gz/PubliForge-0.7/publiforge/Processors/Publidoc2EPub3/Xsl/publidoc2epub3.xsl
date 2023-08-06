<?xml version="1.0" encoding="utf-8"?>
<!-- $Id: publidoc2epub3.xsl baa87d7878d9 2012/08/01 13:54:45 patrick $ -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:import href="publidoc2xhtml_i18n.inc.xsl"/>
  <xsl:import href="publidoc2xhtml_base.inc.xsl"/>
  <xsl:import href="publidoc2xhtml_cals.inc.xsl"/>
  <xsl:import href="publidoc2xhtml_ini.inc.xsl"/>
  <xsl:import href="publidoc2html5_base.inc.xsl"/>
  <xsl:import href="publidoc2html5_ini.inc.xsl"/>
  <xsl:import href="publidoc2epub2_i18n.inc.xsl"/>
  <xsl:import href="publidoc2epub2_base.inc.xsl"/>
  <xsl:import href="publidoc2epub2_ncx.inc.xsl"/>
  <xsl:import href="publidoc2epub3_base.inc.xsl"/>
  <xsl:import href="publidoc2epub3_opf.inc.xsl"/>
  <xsl:import href="publidoc2epub3_nav.inc.xsl"/>

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
  <xsl:param name="aud" select="0"/>
  <xsl:param name="aud_search">%(id)s.%(ext)s</xsl:param>
  <xsl:param name="aud_ext1">.ogg</xsl:param>
  <xsl:param name="aud_ext2">.aac</xsl:param>
  <!-- Processor video parameters -->
  <xsl:param name="vid" select="0"/>
  <xsl:param name="vid_search">%(id)s.%(ext)s</xsl:param>
  <xsl:param name="vid_ext">.ogv</xsl:param>
  <xsl:param name="vid_width">300</xsl:param>
  <!-- Processor ePub 3 parameters -->
  <xsl:param name="subtoc" select="0"/>
  <xsl:param name="js" select="0"/>
  <xsl:param name="ean"/>
  <xsl:param name="cover"/>
  <xsl:param name="publisher_label"/>
  <xsl:param name="publisher_url"/>

  <!-- Variables -->
  <xsl:variable name="path" select="concat($output, 'Container~/EPUB/')"/>
  <xsl:variable name="img_dir">Images/</xsl:variable>
  <xsl:variable name="aud_dir">Audios/</xsl:variable>
  <xsl:variable name="vid_dir">Videos/</xsl:variable>
  <xsl:variable name="html_ext">.xhtml</xsl:variable>
  <xsl:variable name="lang">
    <xsl:choose>
      <xsl:when test="/*/*/@xml:lang">
        <xsl:value-of select="/*/*/@xml:lang"/>
      </xsl:when>
      <xsl:otherwise>en</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>
  <xsl:variable name="onefile" select="0"/>
  <xsl:variable name="toc" select="0"/>


  <xsl:output method="xml" encoding="utf-8" indent="yes"
              doctype-public="" doctype-system="about:legacy-compat"/>
 

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

    <xsl:if test="$img">
      <xsl:choose>
        <xsl:when test="$cover">
          <xsl:apply-templates select="//image[name(..)!='cover']" mode="ini"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:apply-templates select="//image" mode="ini"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:if>
    <xsl:if test="$aud"><xsl:apply-templates select="//audio" mode="ini"/></xsl:if>
    <xsl:if test="$vid"><xsl:apply-templates select="//video" mode="ini"/></xsl:if>

    <xsl:if test=".//note">
      <xsl:call-template name="html_file">
        <xsl:with-param name="name" select="concat($fid, '-not')"/>
        <xsl:with-param name="title" select="$i18n_notes"/>
        <xsl:with-param name="body">
          <body class="pdocDivision">
            <h1><xsl:value-of select="$i18n_notes"/></h1>
          </body>
        </xsl:with-param>
      </xsl:call-template>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      document
      =========================================================================
  -->
  <xsl:template match="document">
    <xsl:call-template name="cover"/>
    <xsl:call-template name="package_opf"/>
    <xsl:call-template name="nav_xhtml"/>
    <xsl:call-template name="toc_ncx"/>

    <xsl:if test="$subtoc">
      <xsl:apply-templates select="division" mode="file"/>
    </xsl:if>
    <xsl:apply-templates select=".//topic" mode="file"/>
  </xsl:template>

  <!--
      =========================================================================
      topic
      =========================================================================
  -->
  <xsl:template match="topic">
    <xsl:call-template name="cover"/>
    <xsl:call-template name="package_opf"/>
    <xsl:call-template name="nav_xhtml"/>
    <xsl:call-template name="toc_ncx"/>

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
  </xsl:template>

</xsl:stylesheet>
