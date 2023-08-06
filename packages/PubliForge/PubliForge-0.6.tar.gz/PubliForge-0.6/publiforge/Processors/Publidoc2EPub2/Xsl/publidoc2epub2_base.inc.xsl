<?xml version="1.0" encoding="utf-8"?>
<!-- $Id: publidoc2epub2_base.inc.xsl aeff1eb899b3 2012/05/23 22:22:20 patrick $ -->
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
              <xsl:value-of select="concat(/*/*/head/title, ' – ', $i18n_title_page)"/>
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
              <xsl:call-template name="anchor_top"/>
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
              <xsl:value-of select="concat(/publidoc/*/head/title, ' – ', $i18n_copyright)"/>
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
              <xsl:value-of select="concat(/*/*/head/title, ' – ')"/>
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
              <xsl:value-of select="concat(/*/*/head/title, ' – ')"/>
            </xsl:if>
            <xsl:choose>
              <xsl:when test="head/title">
                <xsl:apply-templates select="head/title" mode="text"/>
              </xsl:when>
              <xsl:when test="section[1]/head/title">
                <xsl:apply-templates select="section[1]/head/title" mode="text"/>
              </xsl:when>
              <xsl:when test="section[1]/p[1]/initial">
                <xsl:apply-templates select="section[1]/p[1]/initial" mode="text"/>
              </xsl:when>
              <xsl:otherwise>
                <xsl:value-of select="concat($i18n_chapter, ' ', count(preceding::topic)+1)"/>
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
                <xsl:when test="not($subtoc) and not(preceding-sibling::topic) and parent::division/head/title">
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
                                     INLINE LEVEL
      *************************************************************************
  -->
  <!--
      =========================================================================
      number
      =========================================================================
  -->
  <xsl:template match="number">
    <xsl:choose>
      <xsl:when test="@type='roman'">
        <span class="pdocNumberRoman">
          <xsl:value-of select="translate(., 'ivxdl', 'IVXDL')"/>
        </span>
      </xsl:when>
      <xsl:otherwise>
        <span class="pdocNumber"><xsl:apply-templates/></span>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>


  <!--
      =========================================================================
      note
      =========================================================================
  -->
  <xsl:template match="note">
    <a href="{$fid}-not-{count(preceding::note)+1}{$html_ext}" id="n{count(preceding::note)+1}">
      <xsl:choose>
        <xsl:when test="w">
          <xsl:attribute name="class">pdocNoteLink</xsl:attribute>
          <xsl:apply-templates select="w"/>
        </xsl:when>
        <xsl:when test="@label">
          <xsl:attribute name="class">pdocNoteCall</xsl:attribute>
          <sup>(((<xsl:value-of select="@label"/>)))</sup>
        </xsl:when>
        <xsl:otherwise>
          <xsl:attribute name="class">pdocNoteCall</xsl:attribute>
         <sup>(((<xsl:value-of select="count(preceding::note)+1"/>)))</sup>
        </xsl:otherwise>
      </xsl:choose>
    </a>
    <xsl:call-template name="note_file"/>
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
        <xsl:with-param name="title" select="$i18n_cover"/>
        <xsl:with-param name="body">
          <body class="pdocCover">
            <div>
              <xsl:choose>
                <xsl:when test="$cover">
                  <img src="{$img_dir}{$cover}" alt="{$i18n_cover}"/>
                </xsl:when>
                <xsl:when test="head/cover">
                  <img src="{$img_dir}{head/cover/image/@id}{$img_ext}" alt="{$i18n_cover}"/>
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
      <xsl:with-param name="title" select="$i18n_toc"/>
      <xsl:with-param name="body">
        <body class="pdocToc">
          <xsl:if test="head/title">
            <div class="h1"><xsl:apply-templates select="head/title"/></div>
          </xsl:if>
          <div class="h2"><xsl:value-of select="$i18n_toc"/></div>
          <ul>
            <xsl:apply-templates
                select="topic[not(@type='title')]|division" mode="toc"/>
          </ul>
        </body>
      </xsl:with-param>
    </xsl:call-template>
  </xsl:template>

</xsl:stylesheet>
