<?xml version="1.0" encoding="utf-8"?>
<!-- $Id: publidoc2epub_base.inc.xsl 9b28d4eafb24 2012/02/13 18:18:31 patrick $ -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <!--
      *************************************************************************
                                   COMPONENT LEVEL
      *************************************************************************
  -->
  <!--
      =========================================================================
      topic mode file
      =========================================================================
  -->
  <xsl:template match="topic" mode="file">
    <xsl:choose>
      <!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ title ~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
      <xsl:when test="@type='title'">
        <xsl:call-template name="html_file">
          <xsl:with-param name="name"
                          select="concat($fid, '-tpc-', count(preceding::topic)+1)"/>
          <xsl:with-param name="title">
            <xsl:if test="/*/*/head/title">
              <xsl:value-of select="/*/*/head/title"/>
              <xsl-text> - Page de titre</xsl-text>
            </xsl:if>
          </xsl:with-param>
          <xsl:with-param name="body">
            <body class="pdocTopic pdocTopic-title">
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
      </xsl:when>

      <!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ copyright ~~~~~~~~~~~~~~~~~~~~~~~~~ -->
      <xsl:when test="@type='copyright'">
        <xsl:call-template name="html_file">
          <xsl:with-param name="name"
                          select="concat($fid, '-tpc-', count(preceding::topic)+1)"/>
          <xsl:with-param name="title">
            <xsl:if test="/*/*/head/title">
              <xsl:value-of select="/*/*/head/title"/>
              <xsl-text> - Copyright</xsl-text>
            </xsl:if>
          </xsl:with-param>
          <xsl:with-param name="body">
            <body class="pdocTopic pdocTopic-copyright">
              <xsl:call-template name="anchor_top"/>
              <xsl:if test="head/title">
                <div class="h1"><xsl:apply-templates select="head/title"/></div>
              </xsl:if>
              <xsl:if test="head/subtitle">
                <div class="h2"><xsl:apply-templates select="head/subtitle"/></div>
              </xsl:if>
              <xsl:if test="/*/*/head/contributors/contributor[not(role) or role='author']">
                <div class="pdocLabel">Auteurs :</div>
                <ul>
                  <xsl:apply-templates select="/*/*/head/contributors/contributor[not(role) or role='author']"
                                       mode="copyright"/>
                </ul>
              </xsl:if>
              <xsl:if test="/*/*/head/contributors/contributor[role='illustrator']">
                <div class="pdocLabel">Illustrateurs :</div>
                <ul>
                  <xsl:apply-templates select="/*/*/head/contributors/contributor[role='illustrator']"
                                       mode="copyright"/>
                </ul>
              </xsl:if>
              <xsl:apply-templates select="." mode="corpus"/>
            </body>
          </xsl:with-param>
        </xsl:call-template>
      </xsl:when>

      <!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ image ~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
      <xsl:when test="@type='image'">
        <xsl:call-template name="html_file">
          <xsl:with-param name="name"
                          select="concat($fid, '-tpc-', count(preceding::topic)+1)"/>
          <xsl:with-param name="title">
            <xsl:if test="/*/*/head/title">
              <xsl:value-of select="/*/*/head/title"/>
              <xsl-text> - </xsl-text>
            </xsl:if>
            <xsl:value-of select="head/title"/>
          </xsl:with-param>
          <xsl:with-param name="body">
            <body>
              <xsl:attribute name="class">
                <xsl:text>pdocTopic</xsl:text>
                <xsl:if test="@type"> pdocTopic-<xsl:value-of select="@type"/></xsl:if>
              </xsl:attribute>
              <xsl:call-template name="anchor_top"/>
              <xsl:apply-templates select="." mode="corpus"/>
            </body>
          </xsl:with-param>
        </xsl:call-template>
      </xsl:when>

      <!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ others ~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
      <xsl:otherwise>
        <xsl:call-template name="html_file">
          <xsl:with-param name="name"
                          select="concat($fid, '-tpc-', count(preceding::topic)+1)"/>
          <xsl:with-param name="title">
            <xsl:if test="/*/*/head/title">
              <xsl:value-of select="/*/*/head/title"/>
              <xsl-text> - </xsl-text>
            </xsl:if>
            <xsl:choose>
              <xsl:when test="head/title">
                <xsl:apply-templates select="head/title"/>
              </xsl:when>
              <xsl:otherwise>
                <xsl:value-of select="concat('Page ', count(preceding::topic)+1)"/>
              </xsl:otherwise>
            </xsl:choose>
          </xsl:with-param>
          <xsl:with-param name="body">
            <body>
              <xsl:attribute name="class">
                <xsl:text>pdocTopic</xsl:text>
                <xsl:if test="@type"> pdocTopic-<xsl:value-of select="@type"/></xsl:if>
              </xsl:attribute>
              <xsl:call-template name="anchor_top"/>
              <xsl:choose>
                <xsl:when test="head/title">
                  <div class="h1"><xsl:apply-templates select="head/title"/></div>
                  <xsl:if test="head/subtitle">
                    <div class="h2"><xsl:apply-templates select="head/subtitle"/></div>
                  </xsl:if>
                </xsl:when>
                <xsl:when test="not(preceding-sibling::topic) and parent::division/head/title">
                  <div class="h1"><xsl:apply-templates select="parent::division/head/title"/></div>
                  <xsl:if test="parent::division/head/subtitle">
                    <div class="h2"><xsl:apply-templates select="parent::division/head/subtitle"/></div>
                  </xsl:if>
                </xsl:when>
              </xsl:choose>
              <xsl:apply-templates select="." mode="corpus"/>
            </body>
          </xsl:with-param>
        </xsl:call-template>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="contributor" mode="copyright">
    <li>
      <xsl:apply-templates select="firstname"/>
      <xsl:text> </xsl:text>
      <xsl:apply-templates select="lastname"/>
    </li>
  </xsl:template>

  <xsl:template name="anchor_top">
    <div>
      <a id="top"><xsl:text> </xsl:text></a>
      <a id="div1"><xsl:text> </xsl:text></a>
      <a id="div2"><xsl:text> </xsl:text></a>
      <a id="div3"><xsl:text> </xsl:text></a>
    </div>
 </xsl:template>

  <!--
      *************************************************************************
                                      BLOCK LEVEL
      *************************************************************************
  -->
  <!--
      ========================================================================
      media
      ========================================================================
  -->
  <xsl:template match="audio">
    <div class="pdocAudio">-- Son --</div>
  </xsl:template>


  <!--
      *************************************************************************
                                 CALLABLE TEMPLATES
      *************************************************************************
  -->

  <!--
      =========================================================================
      Template cover
      =========================================================================
  -->
  <xsl:template name="cover">
    <xsl:if test="head/cover or $cover">
      <xsl:call-template name="html_file">
        <xsl:with-param name="name" select="concat($fid, '-cover')"/>
        <xsl:with-param name="title">Couverture</xsl:with-param>
        <xsl:with-param name="body">
          <body class="pdocCover">
            <div>
              <xsl:choose>
                <xsl:when test="$cover">
                  <img src="{$img_dir}{$cover}" alt="Couverture"/>
                </xsl:when>
                <xsl:when test="head/cover">
                  <img src="{$img_dir}{head/cover/image/@id}{$img_ext}"
                       alt="Couverture"/>
                </xsl:when>
              </xsl:choose>
            </div>
          </body>
        </xsl:with-param>
      </xsl:call-template>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      Template toc
      =========================================================================
  -->
  <xsl:template name="toc">
    <xsl:call-template name="html_file">
      <xsl:with-param name="name" select="concat($fid, '-toc')"/>
      <xsl:with-param name="title">Sommaire</xsl:with-param>
      <xsl:with-param name="body">
        <body class="pdocToc">
          <xsl:if test="head/title">
            <div class="h1"><xsl:apply-templates select="head/title"/></div>
          </xsl:if>
          <div class="h2">Sommaire</div>
          <ul>
            <xsl:apply-templates
                select="topic[not(@type='title')]|division" mode="toc"/>
          </ul>
        </body>
      </xsl:with-param>
    </xsl:call-template>
  </xsl:template>

</xsl:stylesheet>
