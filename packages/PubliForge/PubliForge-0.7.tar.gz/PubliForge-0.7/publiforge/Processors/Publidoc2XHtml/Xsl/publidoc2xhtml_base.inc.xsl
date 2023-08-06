<?xml version="1.0" encoding="utf-8"?>
<!-- $Id: publidoc2xhtml_base.inc.xsl ee920e02dd89 2012/08/09 17:09:39 patrick $ -->
<xsl:stylesheet version="1.1" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:date="http://exslt.org/dates-and-times"
                extension-element-prefixes="date">

  <!--
      *************************************************************************
                                   DIVISION LEVEL
      *************************************************************************
  -->
  <!--
      =========================================================================
      division mode onefile
      =========================================================================
  -->
  <xsl:template match="division" mode="onefile">
    <div class="pdocDivision">
      <xsl:if test="head/title">
        <xsl:choose>
          <xsl:when test="count(ancestor::division)=0">
            <h2><xsl:apply-templates select="head/title"/></h2>
          </xsl:when>
          <xsl:otherwise>
            <h3><xsl:apply-templates select="head/title"/></h3>
          </xsl:otherwise>
        </xsl:choose>
        <xsl:if test="head/subtitle">
          <xsl:choose>
            <xsl:when test="count(ancestor::division)=0">
              <h3><xsl:apply-templates select="head/subtitle"/></h3>
            </xsl:when>
            <xsl:otherwise>
              <h4><xsl:apply-templates select="head/subtitle"/></h4>
            </xsl:otherwise>
          </xsl:choose>
        </xsl:if>
      </xsl:if>
      <xsl:apply-templates mode="onefile"/>
    </div>
  </xsl:template>

  <xsl:template match="head|file|link" mode="onefile"/>

  <!--
      =========================================================================
      division mode maintoc & toc
      =========================================================================
  -->
  <xsl:template match="division" mode="maintoc">
    <li>
      <a href="{$fid}-div-{count(preceding::division)+1}{$html_ext}">
        <xsl:choose>
          <xsl:when test="head/title">
            <xsl:apply-templates select="head/title"/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:value-of select="concat($i18n_part, ' ', count(preceding::topic)+1)"/>
          </xsl:otherwise>
        </xsl:choose>
        <xsl:if test="head/subtitle"> — </xsl:if>
        <xsl:apply-templates select="head/subtitle"/>
      </a>
      <xsl:if test="head/abstract">
        <div class="pdocAbstract">
          <xsl:apply-templates select="head/abstract"/>
        </div>
      </xsl:if>
      <ul>
        <xsl:apply-templates mode="toc"/>
      </ul>
    </li>
  </xsl:template>

  <xsl:template match="division" mode="toc">
    <li>
      <div>
        <xsl:choose>
          <xsl:when test="head/title">
            <xsl:apply-templates select="head/title"/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:value-of select="concat($i18n_part, ' ', count(preceding::division)+1)"/>
          </xsl:otherwise>
        </xsl:choose>
        <xsl:if test="head/subtitle"> — </xsl:if>
        <xsl:apply-templates select="head/subtitle"/>
      </div>
      <ul>
        <xsl:apply-templates mode="toc"/>
      </ul>
    </li>
  </xsl:template>

  <xsl:template match="head" mode="toc"/>

  <!--
      =========================================================================
      division mode file
      =========================================================================
  -->
  <xsl:template match="division" mode="file">
    <xsl:if test="not(ancestor::division)">
      <xsl:call-template name="html_file">
        <xsl:with-param name="name"
                        select="concat($fid, '-div-', count(preceding::division)+1)"/>

        <xsl:with-param name="title">
          <xsl:if test="/*/*/head/title">
            <xsl:apply-templates select="/*/*/head/title" mode="text"/>
            <xsl-text> – </xsl-text>
          </xsl:if>
          <xsl:choose>
            <xsl:when test="head/title">
              <xsl:apply-templates select="head/title" mode="text"/>
            </xsl:when>
            <xsl:otherwise>
              <xsl:value-of select="concat($i18n_part, ' ', count(preceding::division)+1)"/>
            </xsl:otherwise>
          </xsl:choose>
        </xsl:with-param>

        <xsl:with-param name="body">
          <body class="pdocToc pdocDivision">
            <h1>
              <xsl:choose>
                <xsl:when test="head/title">
                  <xsl:apply-templates select="head/title"/>
                </xsl:when>
                <xsl:otherwise>
                  <xsl:value-of select="concat($i18n_part, ' ', count(preceding::division)+1)"/>
                </xsl:otherwise>
              </xsl:choose>
            </h1>
            <xsl:if test="head/subtitle">
              <h2><xsl:apply-templates select="head/subtitle"/></h2>
            </xsl:if>
            <ul>
              <xsl:apply-templates mode="toc"/>
            </ul>
          </body>
        </xsl:with-param>
      </xsl:call-template>
    </xsl:if>
  </xsl:template>


  <!--
      *************************************************************************
                                   COMPONENT LEVEL
      *************************************************************************
  -->
  <!--
      =========================================================================
      topic mode onefile
      =========================================================================
  -->
  <xsl:template match="topic" mode="onefile">
    <div>
      <xsl:attribute name="class">
        <xsl:text>pdocTopic</xsl:text>
        <xsl:if test="@type"> pdocTopic-<xsl:value-of select="@type"/></xsl:if>
      </xsl:attribute>
      <xsl:if test="head/title">
        <xsl:choose>
          <xsl:when test="count(ancestor::division)=0">
            <h3><xsl:apply-templates select="head/title"/></h3>
          </xsl:when>
          <xsl:otherwise>
            <h4><xsl:apply-templates select="head/title"/></h4>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:if>
      <xsl:if test="head/subtitle">
        <h5><xsl:apply-templates select="head/subtitle"/></h5>
      </xsl:if>
      <xsl:apply-templates select="." mode="corpus"/>
    </div>
  </xsl:template>

  <!--
      =========================================================================
      topic mode maintoc & toc
      =========================================================================
  -->
  <xsl:template match="topic" mode="maintoc">
    <xsl:apply-templates select="." mode="toc"/>
  </xsl:template>

  <xsl:template match="topic" mode="toc">
    <li>
      <a href="{$fid}-tpc-{count(preceding::topic)+1}{$html_ext}">
        <xsl:choose>
          <xsl:when test="head/title">
            <xsl:apply-templates select="head/title"/>
          </xsl:when>
          <xsl:when test="section[1]/head/title">
            <xsl:apply-templates select="section[1]/head/title"/>
          </xsl:when>
          <xsl:when test="section[1]/p[1]/initial">
            <xsl:apply-templates select="section[1]/p[1]/initial" mode="toc"/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:value-of select="concat($i18n_chapter, ' ', count(preceding::topic)+1)"/>
          </xsl:otherwise>
        </xsl:choose>
        <xsl:if test="head/subtitle"> • </xsl:if>
        <xsl:apply-templates select="head/subtitle"/>
      </a>
      <xsl:if test="head/abstract">
        <div class="pdocAbstract">
          <xsl:apply-templates select="head/abstract"/>
        </div>
      </xsl:if>
    </li>
  </xsl:template>

  <!--
      =========================================================================
      topic mode file
      =========================================================================
  -->
  <xsl:template match="topic" mode="file">
    <xsl:call-template name="html_file">
      <xsl:with-param name="name"
                      select="concat($fid, '-tpc-', count(preceding::topic)+1)"/>

      <xsl:with-param name="title">
        <xsl:if test="/*/*/head/title">
          <xsl:apply-templates select="/*/*/head/title" mode="text"/>
          <xsl-text> - </xsl-text>
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
          <xsl:call-template name="navigation"/>

          <xsl:choose>
            <xsl:when test="head/title">
              <h1><xsl:apply-templates select="head/title"/></h1>
              <xsl:if test="head/subtitle">
                <h2><xsl:apply-templates select="head/subtitle"/></h2>
              </xsl:if>
            </xsl:when>
            <xsl:when test="not($subtoc) and not(preceding-sibling::topic)
                            and parent::division/head/title">
              <h1><xsl:apply-templates select="parent::division/head/title"/></h1>
              <xsl:if test="parent::division/head/subtitle">
                <h2><xsl:apply-templates select="parent::division/head/subtitle"/></h2>
              </xsl:if>
            </xsl:when>
          </xsl:choose>
          <xsl:apply-templates select="." mode="corpus"/>
        </body>
      </xsl:with-param>
    </xsl:call-template>
  </xsl:template>
  
  <!--
      =========================================================================
      topic mode corpus
      =========================================================================
  -->
  <xsl:template match="topic" mode="corpus">
    <xsl:apply-templates select="section"/>
  </xsl:template>

  <!--
      =========================================================================
      file mode toc
      =========================================================================
  -->
  <xsl:template match="file" mode="toc">
    <li>
      <a>
        <xsl:attribute name="href">
          <xsl:choose>
            <xsl:when test="@uri"><xsl:value-of select="@uri"/></xsl:when>
            <xsl:otherwise>
              <xsl:value-of select="concat(substring-before(@name, '.xml'), $html_ext)"/>
            </xsl:otherwise>
          </xsl:choose>
        </xsl:attribute>
        <xsl:choose>
          <xsl:when test="text()"><xsl:apply-templates/></xsl:when>
          <xsl:when test="@uri"><xsl:value-of select="@uri"/></xsl:when>
          <xsl:otherwise><xsl:value-of select="@name"/></xsl:otherwise>
        </xsl:choose>
      </a>
    </li>
   </xsl:template>

  <!--
      =========================================================================
      link mode toc
      =========================================================================
  -->
  <xsl:template match="link" mode="toc">
    <li><xsl:apply-templates select="."/></li>
  </xsl:template>


  <!--
      *************************************************************************
                                   SECTION LEVEL
      *************************************************************************
  -->
  <!--
      ========================================================================
      section
      ========================================================================
  -->
  <xsl:template match="section">
    <div>
      <xsl:attribute name="class">
        <xsl:choose>
          <xsl:when test="count(preceding-sibling::section)=0
                          and count(ancestor::section/preceding-sibling::section)=0">
            <xsl:value-of select="concat('pdocSection', count(ancestor::section)+1, ' first')"/>
          </xsl:when>
          <xsl:otherwise>
             <xsl:value-of select="concat('pdocSection', count(ancestor::section)+1)"/>
         </xsl:otherwise>
        </xsl:choose>
        <xsl:if test="@type"> pdocSection-<xsl:value-of select="@type"/></xsl:if>
      </xsl:attribute>

      <xsl:if test="head/title">
        <div class="pdocSectionTitle">
          <xsl:apply-templates select="head/title"/>
        </div>
      </xsl:if>
      <xsl:if test="head/subtitle">
        <div class="pdocSectionSubtitle">
          <xsl:apply-templates select="head/subtitle"/>
        </div>
      </xsl:if>

      <xsl:apply-templates
          select="section|p|speech|list|blockquote|table|media"/>

      <xsl:if test="$aud and head/audio[@type='background']">
        <xsl:call-template name="audio">
          <xsl:with-param name="id" select="head/audio[@type='background']/@id"/>
          <xsl:with-param name="controls" select="0"/>
          <xsl:with-param name="autoplay" select="1"/>
        </xsl:call-template>
      </xsl:if>
    </div>
  </xsl:template>


  <!--
      *************************************************************************
                                      BLOCK LEVEL
      *************************************************************************
  -->
  <!--
      =========================================================================
      p
      =========================================================================
  -->
  <xsl:template match="p">
    <span>
      <xsl:attribute name="class">
        <xsl:text>pdocP</xsl:text>
        <xsl:if test="position()=1">
          <xsl:text> first</xsl:text>
        </xsl:if>
      </xsl:attribute>
      <xsl:apply-templates/><br/>
    </span>
  </xsl:template>

  <xsl:template match="p" mode="text">
    <xsl:apply-templates mode="text"/><xsl:text> </xsl:text>
  </xsl:template>

  <!--
      =========================================================================
      speech
      =========================================================================
  -->
  <xsl:template match="speaker">
    <strong class="pdocSpeechSpeaker"><xsl:apply-templates/></strong>
    <xsl:if test="../stage">, </xsl:if>
  </xsl:template>

  <xsl:template match="stage">
    <span class="pdocSpeechStage"><em><xsl:apply-templates/></em></span>
  </xsl:template>

  <!--
      =========================================================================
      list
      =========================================================================
  -->
  <xsl:template match="list">
    <xsl:if test="head/title">
      <div class="pdocListTitle"><xsl:apply-templates select="head/title"/></div>
    </xsl:if>
    <xsl:if test="head/subtitle">
      <div class="pdocListSubtitle"><xsl:apply-templates select="head/subtitle"/></div>
    </xsl:if>
    <xsl:choose>
      <xsl:when test="@type='ordered'">
        <ol class="pdocList">
          <xsl:apply-templates select="item"/>
        </ol>
      </xsl:when>
      <xsl:when test="@type='glossary'">
        <ul class="pdocListGlossary">
          <xsl:apply-templates select="item"/>
        </ul>
      </xsl:when>
      <xsl:otherwise>
        <ul class="pdocList">
          <xsl:apply-templates select="item"/>
        </ul>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="item">
    <li><xsl:apply-templates/></li>
  </xsl:template>

  <xsl:template match="label">
    <strong class="pdocLabel"><xsl:apply-templates/></strong>
  </xsl:template>

  <!--
      =========================================================================
      blockquote
      =========================================================================
  -->
  <xsl:template match="blockquote">
    <div class="pdocQuote">
      <xsl:if test="head/title">
        <div class="pdocQuoteTitle"><xsl:apply-templates select="head/title"/></div>
      </xsl:if>
      <xsl:if test="head/subtitle">
        <div class="pdocQuoteSubtitle"><xsl:apply-templates select="head/subtitle"/></div>
      </xsl:if>
      <xsl:apply-templates select="p|speech|list"/>
      <xsl:if test="attribution">
        <div class="pdocQuoteAttribution">
          <xsl:apply-templates select="attribution"/>
        </div>
      </xsl:if>
    </div>
  </xsl:template>

  <!--
      =========================================================================
      media
      =========================================================================
  -->
  <xsl:template match="media">
    <xsl:choose>
      <xsl:when test="($img and image) or ($aud and audio) or ($vid and video)">
        <div class="pdocMedia">
          <xsl:if test="head/title">
            <div class="pdocMediaTitle"><xsl:apply-templates select="head/title"/></div>
          </xsl:if>
          <xsl:if test="head/subtitle">
            <div class="pdocMediaSubtitle"><xsl:apply-templates select="head/subtitle"/></div>
          </xsl:if>
          <xsl:apply-templates select="image|audio|video" mode="media"/>
          <xsl:apply-templates select="caption"/>
        </div>
      </xsl:when>
      <xsl:otherwise> </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="caption">
    <xsl:choose>
      <xsl:when test="@x or @y">
        <div class="pdocMediaCaptionAbsolute">
          <xsl:attribute name="style">
            <xsl:if test="@x">left:<xsl:value-of select="@x"/>;</xsl:if>
            <xsl:if test="@y">top:<xsl:value-of select="@y"/>;</xsl:if>
          </xsl:attribute>
          <xsl:apply-templates/>
        </div>
      </xsl:when>
      <xsl:otherwise>
        <div class="pdocMediaCaption"><xsl:apply-templates/></div>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!--
      =========================================================================
      image
      =========================================================================
  -->
  <xsl:template match="image">
    <xsl:choose>
      <xsl:when test="ancestor::tooltip">
        <img src="{$img_dir}{@id}.png"><xsl:call-template name="alt"/></img>
      </xsl:when>
      <xsl:otherwise>
        <img src="{$img_dir}{@id}{$img_ext}" class="pdocIcon">
          <xsl:call-template name="alt"/>
        </img>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="image" mode="media">
    <xsl:if test="$img">
      <div>
        <xsl:attribute name="class">
          <xsl:text>pdocImage</xsl:text>
          <xsl:if test="@type"> pdocImage-<xsl:value-of select="@type"/></xsl:if>
          <xsl:if test="hotspot"> hotspot</xsl:if>
          <xsl:if test="$js and tooltip"> tooltip</xsl:if>
        </xsl:attribute>
        <xsl:choose>
          <xsl:when test="../link">
            <a>
              <xsl:apply-templates select="../link" mode="href"/>
              <img src="{$img_dir}{@id}{$img_ext}"><xsl:call-template name="alt"/></img>
            </a>
          </xsl:when>
          <xsl:otherwise>
            <img src="{$img_dir}{@id}{$img_ext}"><xsl:call-template name="alt"/></img>
          </xsl:otherwise>
        </xsl:choose>
        <xsl:apply-templates select="hotspot|tooltip"/>
      </div>
      <xsl:if test="hotspot or ($js and tooltip)">
        <div class="clear"><xsl:text> </xsl:text></div>
      </xsl:if>
      <xsl:if test="copyright">
        <div class="pdocMediaCopyright">
          <xsl:apply-templates select="copyright"/>
        </div>
      </xsl:if>
    </xsl:if>
  </xsl:template>

  <xsl:template match="tooltip">
    <xsl:if test="$js">
      <div class="pdocImageTooltip" id="pulse{count(preceding::tooltip)+1}t">
        <xsl:attribute name="style">
          <xsl:text>left:</xsl:text>
          <xsl:choose>
            <xsl:when test="@dx">
              <xsl:value-of
                  select="concat(translate(substring-before(@x, '%')+@dx, ',', '.'), '%')"/>
            </xsl:when>
            <xsl:otherwise><xsl:value-of select="@x"/></xsl:otherwise>
          </xsl:choose>
          <xsl:text>; top:</xsl:text>
          <xsl:choose>
            <xsl:when test="@dy">
               <xsl:value-of
                  select="concat(translate(substring-before(@y, '%')+@dy, ',', '.'), '%')"/>
            </xsl:when>
            <xsl:otherwise><xsl:value-of select="@y"/></xsl:otherwise>
          </xsl:choose>
          <xsl:text>;</xsl:text>
        </xsl:attribute>
        <xsl:apply-templates/>
      </div>
      <div class="pdocImagePulse" id="pulse{count(preceding::tooltip)+1}">
        <xsl:attribute name="style">
          <xsl:value-of select="concat('left:', @x, '; top:', @y, ';')"/>
        </xsl:attribute>
        <img src="Images/pulse.gif" alt="pulse"/>
      </div>
    </xsl:if>
  </xsl:template>
  
  <xsl:template match="hotspot">
    <xsl:if test="link or ($aud and audio) or ($vid and video)">
      <div class="pdocImageHotspot">
        <xsl:attribute name="style">
          <xsl:value-of select="concat('left:', @x, '; top:', @y, ';')"/>
          <xsl:if test="link and @width">
            <xsl:value-of select="concat('width:', @width, '; height:', @height, ';')"/>
          </xsl:if>
        </xsl:attribute>
        <xsl:choose>
          <xsl:when test="link">
            <a>
              <xsl:apply-templates select="link" mode="href"/>
              <xsl:if test="@width">
                <xsl:attribute name="style">width:100%; height:100%;</xsl:attribute>
              </xsl:if>
              <xsl:apply-templates select="link" mode="content"/>
            </a>
          </xsl:when>
          <xsl:when test="audio">
            <xsl:call-template name="audio">
              <xsl:with-param name="id" select="audio/@id"/>
            </xsl:call-template>
          </xsl:when>
          <xsl:when test="video">
            <xsl:call-template name="video">
              <xsl:with-param name="id" select="video/@id"/>
              <xsl:with-param name="width" select="$vid_width"/>
            </xsl:call-template>
          </xsl:when>
        </xsl:choose>
      </div>
    </xsl:if>
  </xsl:template>

  <xsl:template name="alt">
    <xsl:attribute name="alt">
      <xsl:choose>
        <xsl:when test="../head/title">
          <xsl:apply-templates select="../head/title" mode="text"/>
        </xsl:when>
        <xsl:otherwise><xsl:value-of select="@id"/></xsl:otherwise>
      </xsl:choose>
    </xsl:attribute>
  </xsl:template>

  <!--
      =========================================================================
      audio
      =========================================================================
  -->
  <xsl:template match="audio" mode="media">
    <xsl:if test="$aud">
      <xsl:choose>
        <xsl:when test="@type='background'">
          <xsl:call-template name="audio">
            <xsl:with-param name="controls" select="0"/>
            <xsl:with-param name="autoplay" select="1"/>
          </xsl:call-template>
        </xsl:when>
        <xsl:otherwise><xsl:call-template name="audio"/></xsl:otherwise>
      </xsl:choose>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      video
      =========================================================================
  -->
  <xsl:template match="video" mode="media">
    <xsl:if test="$vid">
      <xsl:call-template name="video"/>
    </xsl:if>
  </xsl:template>


  <!--
      *************************************************************************
                                     INLINE LEVEL
      *************************************************************************
  -->
  <!--
      =========================================================================
      math
      =========================================================================
  -->
  <xsl:template match="sub|sup">
    <xsl:copy><xsl:apply-templates/></xsl:copy>
  </xsl:template>

  <xsl:template match="var">
    <em class="pdocVar"><xsl:apply-templates/></em>
  </xsl:template>

  <xsl:template match="math">
    <xsl:choose>
      <xsl:when test="@wide='true'">
        <span class="pdocMathWide"><xsl:apply-templates/></span>
      </xsl:when>
      <xsl:otherwise>
        <span class="pdocMath"><xsl:apply-templates/></span>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!--
      =========================================================================
      number
      =========================================================================
  -->
  <xsl:template match="number">
    <span>
      <xsl:attribute name="class">
        <xsl:choose>
          <xsl:when test="@type='roman'">pdocNumberRoman</xsl:when>
          <xsl:otherwise>pdocNumber</xsl:otherwise>
        </xsl:choose>
      </xsl:attribute>
      <xsl:apply-templates/>
    </span>
  </xsl:template>

  <!--
      =========================================================================
      date
      =========================================================================
  -->
  <xsl:template match="date">
    <xsl:choose>
      <xsl:when test="not(text())">
        <xsl:choose>
          <xsl:when test="string-length(@value)=4">
            <xsl:value-of select="@value"/>
          </xsl:when>
          <xsl:when test="string-length(@value)=7">
            <xsl:value-of select="substring(@value, 6, 2)"/>
            <xsl:text>/</xsl:text>
            <xsl:value-of select="substring(@value, 1, 4)"/>
          </xsl:when>
          <xsl:when test="string-length(@value)=10">
            <xsl:value-of select="substring(@value, 9, 2)"/>
            <xsl:text>/</xsl:text>
            <xsl:value-of select="substring(@value, 6, 2)"/>
            <xsl:text>/</xsl:text>
            <xsl:value-of select="substring(@value, 1, 4)"/>
          </xsl:when>
        </xsl:choose>
      </xsl:when>
      <xsl:otherwise><xsl:apply-templates/></xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!--
      =========================================================================
      note
      =========================================================================
  -->
  <xsl:template match="note">
    <xsl:choose>
      <xsl:when test="$onefile">
        <a href="#n{count(preceding::note)+1}" id="nc{count(preceding::note)+1}" class="pdocNoteCall">
          <xsl:apply-templates select="." mode="call"/>
        </a>
      </xsl:when>
      <xsl:otherwise>
        <a href="{$fid}-not-{count(preceding::note)+1}{$html_ext}" id="n{count(preceding::note)+1}">
          <xsl:apply-templates select="." mode="call"/>
        </a>
        <xsl:call-template name="note_file"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
  
  <xsl:template match="note" mode="call">
    <xsl:choose>
      <xsl:when test="w">
        <xsl:attribute name="class">pdocNoteLink</xsl:attribute>
        <xsl:attribute name="title">
          <xsl:for-each select="p">
            <xsl:value-of select="normalize-space()"/><xsl:text> </xsl:text>
          </xsl:for-each>
        </xsl:attribute>
        <xsl:apply-templates select="w"/>
      </xsl:when>
      <xsl:when test="@label">
        <xsl:attribute name="class">pdocNoteCall</xsl:attribute>
        <xsl:attribute name="title"><xsl:value-of select="normalize-space()"/></xsl:attribute>
        <sup>(<xsl:value-of select="@label"/>)</sup>
      </xsl:when>
      <xsl:otherwise>
        <xsl:attribute name="class">pdocNoteCall</xsl:attribute>
        <xsl:attribute name="title"><xsl:value-of select="normalize-space()"/></xsl:attribute>
        <sup>(<xsl:value-of select="count(preceding::note)+1"/>)</sup>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
  
  <xsl:template match="note" mode="title">
    <xsl:choose>
      <xsl:when test="w">
        <xsl:apply-templates select="w" mode="text"/>
      </xsl:when>
      <xsl:when test="@label">
        <xsl:value-of select="concat($i18n_note, ' ', @label)"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="concat($i18n_note, ' ', count(preceding::note)+1)"/>
      </xsl:otherwise>
    </xsl:choose>    
  </xsl:template>
  
  <xsl:template match="note" mode="footer">
    <div>
      <a href="#nc{count(preceding::note)+1}" id="n{count(preceding::note)+1}">
        <xsl:apply-templates select="." mode="title"/>
        <xsl:text>. </xsl:text>
      </a>
      <xsl:apply-templates select="*[name()!='w']|text()"/>
    </div>
  </xsl:template>

  <xsl:template match="note" mode="text"/>

  <xsl:template name="note_file">
    <xsl:call-template name="html_file">
      <xsl:with-param name="name">
        <xsl:value-of select="concat($fid, '-not-', count(preceding::note)+1)"/>
      </xsl:with-param>
      <xsl:with-param name="title">
        <xsl:apply-templates select="." mode="title"/>
      </xsl:with-param>
      <xsl:with-param name="body">
        <body class="pdocNote">
          <h1><xsl:apply-templates select="." mode="title"/></h1>
          <div class="pdocNoteText">
            <xsl:apply-templates select="*[name()!='w']|text()"/>
          </div>
          <div class="pdocNoteBack">
            <a href="{$fid}-tpc-{count(preceding::topic)+1}{$html_ext}#n{count(preceding::note)+1}">
              <xsl:value-of select="concat('— ', $i18n_back, ' —')"/>
            </a>
          </div>
        </body>
      </xsl:with-param>
    </xsl:call-template>
  </xsl:template>

  <!--
      =========================================================================
      quote
      =========================================================================
  -->
  <xsl:template match="quote">
    <xsl:text>« </xsl:text>
    <em class="pdocQuote"><xsl:apply-templates/></em>
    <xsl:text> »</xsl:text>
  </xsl:template>

  <!--
      =========================================================================
      link, anchor
      =========================================================================
  -->
  <xsl:template match="link">
    <a class="pdocLink">
      <xsl:apply-templates select="." mode="href"/>
      <xsl:apply-templates select="." mode="content"/>
    </a>
  </xsl:template>

  <xsl:template match="link" mode="href">
    <xsl:attribute name="href">
      <xsl:choose>
        <xsl:when test="@idref">
          <xsl:call-template name="link_idref">
            <xsl:with-param name="target" select="id(@idref)"/>
          </xsl:call-template>
        </xsl:when>
        <xsl:otherwise><xsl:value-of select="@uri"/></xsl:otherwise>
      </xsl:choose>
    </xsl:attribute>
  </xsl:template>
  
  <xsl:template name="link_idref">
    <xsl:param name="target"/>
    <xsl:choose>
      <xsl:when test="$onefile or count(preceding::topic)=count($target/preceding::topic)">
        <xsl:value-of select="concat('#', $target/@xml:id)"/>
      </xsl:when>
      <xsl:when test="name($target)='topic'">
        <xsl:value-of
            select="concat($fid, '-tpc-', count($target/preceding::topic)+1, $html_ext)"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of
            select="concat($fid, '-tpc-', count($target/preceding::topic)+1, $html_ext,
                    '#', $target/@xml:id)"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="link" mode="content">
    <xsl:choose>
      <xsl:when test="normalize-space() or node()"><xsl:apply-templates/></xsl:when>
      <xsl:when test="ancestor::hotspot"><xsl:text> </xsl:text></xsl:when>
      <xsl:when test="@idref"><xsl:value-of select="@idref"/></xsl:when>
      <xsl:otherwise><xsl:value-of select="@uri"/></xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="anchor"><a id="{@xml:id}"><xsl:text> </xsl:text></a></xsl:template>

  <!--
      =========================================================================
      initial
      =========================================================================
  -->
  <xsl:template match="initial">
    <span class="pdocInitialCap">
      <xsl:apply-templates select="c"/>
    </span>
    <xsl:if test="w">
      <span class="pdocInitialWords"><xsl:apply-templates select="w"/></span>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      smil
      =========================================================================
  -->
  <xsl:template match="smil">
    <span id="s{count(preceding::smil)-count(ancestor::topic/preceding::smil)+1}">
      <xsl:apply-templates/>
    </span>
  </xsl:template>

  <!--
      =========================================================================
      Miscellaneous
      =========================================================================
  -->
  <xsl:template match="name">
    <em class="pdocName"><xsl:apply-templates/></em>
  </xsl:template>

  <xsl:template match="foreign">
    <em class="pdocForeign"><xsl:apply-templates/></em>
  </xsl:template>

  <xsl:template match="highlight">
    <strong class="pdocHighlight"><xsl:apply-templates/></strong>
  </xsl:template>

  <xsl:template match="mentioned">
    <em class="pdocMentioned"><xsl:apply-templates/></em>
  </xsl:template>

  <xsl:template match="acronym">
    <span class="pdocAcronym"><xsl:apply-templates/></span>
  </xsl:template>

  <xsl:template match="term">
    <em class="pdocTerm"><xsl:apply-templates/></em>
  </xsl:template>


  <!--
      *************************************************************************
                                 CALLABLE TEMPLATES
      *************************************************************************
  -->
  <!--
      =========================================================================
      Template html_file
      =========================================================================
  -->
  <xsl:template name="html_file">
    <xsl:param name="name"/>
    <xsl:param name="title"/>
    <xsl:param name="body"/>
    <xsl:document href="{$path}{$name}{$html_ext}" method="xml"
                  encoding="utf-8" indent="yes"
                  doctype-public="-//W3C//DTD XHTML 1.1//EN"
                  doctype-system="http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
      <xsl:call-template name="html_frame">
        <xsl:with-param name="title" select="$title"/>
        <xsl:with-param name="body" select="$body"/>
      </xsl:call-template>
    </xsl:document>
  </xsl:template>

  <!--
      =========================================================================
      Template html_frame
      =========================================================================
  -->
  <xsl:template name="html_frame">
    <xsl:param name="title"/>
    <xsl:param name="body"/>
    <xsl:comment> Generated by PubliForge, <xsl:value-of select="date:date-time()"/> </xsl:comment>
    <html xmlns="http://www.w3.org/1999/xhtml">
      <xsl:attribute name="xml:lang"><xsl:value-of select="$lang"/></xsl:attribute>
      <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
        <meta http-equiv="Content-Language">
          <xsl:attribute name="content"><xsl:value-of select="$lang"/></xsl:attribute>
        </meta>
        <title><xsl:value-of select="$title"/></title>
        <link rel="StyleSheet" href="Css/reset.css" type="text/css"/>
        <link rel="StyleSheet" href="Css/publidoc.css" type="text/css"/>
        <link rel="StyleSheet" href="Css/custom.css" type="text/css"/>
        <xsl:if test="$js and (name()='topic' or $onefile)">
          <script src="Js/mootools.js" type="text/javascript"><xsl:text> </xsl:text></script>
          <script src="Js/publidoc.js" type="text/javascript"><xsl:text> </xsl:text></script>
        </xsl:if>
      </head>
      <xsl:copy-of select="$body"/>
    </html>
  </xsl:template>

  <!--
      =========================================================================
      Template audio
      =========================================================================
  -->
  <xsl:template name="audio">
    <xsl:param name="id" select="@id"/>
    <xsl:param name="controls" select="1"/>
    <xsl:param name="autoplay" select="0"/>
    <xsl:if test="$controls">
      <div>
        <xsl:attribute name="class">
          <xsl:text>pdocAudio</xsl:text>
          <xsl:if test="name()='audio' and @type"> pdocAudio-<xsl:value-of select="@type"/></xsl:if>
        </xsl:attribute>
        <a href="{$aud_dir}{$id}{$aud_ext}">Son</a>
      </div>
    </xsl:if>
  </xsl:template>
  
  <!--
      =========================================================================
      Template video
      =========================================================================
  -->
  <xsl:template name="video">
    <xsl:param name="id" select="@id"/>
    <xsl:param name="controls" select="1"/>
    <xsl:param name="autoplay" select="0"/>
    <xsl:param name="width"/>
    <xsl:if test="$controls">
      <div>
        <xsl:attribute name="class">
          <xsl:text>pdocVideo</xsl:text>
          <xsl:if test="name()='video' and @type"> pdocVideo-<xsl:value-of select="@type"/></xsl:if>
        </xsl:attribute>
        <a href="{$vid_dir}{$id}{$vid_ext}">Video</a>
      </div>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      Template navigation
      =========================================================================
  -->
  <xsl:template name="navigation">
    <div class="pdocNavBar col111">
      <div class="colFirst">
        <xsl:if test="count(preceding::topic)">
          <a href="{$fid}-tpc-{count(preceding::topic)}{$html_ext}">
            <img src="{$img_dir}go_previous.png" alt="Previous"/>
          </a>
        </xsl:if>
        <xsl:text> </xsl:text>
      </div>
      <div class="col">
        <a href="{$fid}{$html_ext}">
          <img src="{$img_dir}go_up.png" alt="up"/>
        </a>
      </div>
      <div class="colLast">
        <xsl:if test="count(following::topic)">
          <a href="{$fid}-tpc-{count(preceding::topic)+2}{$html_ext}">
            <img src="{$img_dir}go_next.png" alt="Next"/>
          </a>
        </xsl:if>
        <xsl:text> </xsl:text>
      </div>
      <hr/>
    </div>
  </xsl:template>
  
  <!--
      =========================================================================
      Template tokenize
      =========================================================================
  -->
  <xsl:template name="tokenize">
    <xsl:param name="text"/>
    <xsl:value-of select="translate($text,
                          'àâäæçéèêëîïôöœùûüÀÂÄÆÇÉÈÊËÎÏÔÖŒÙÛÜ',
                          'aaaaceeeeiiooouuuAAAACEEEEIIOOOUUU')"/>
  </xsl:template>
</xsl:stylesheet>
