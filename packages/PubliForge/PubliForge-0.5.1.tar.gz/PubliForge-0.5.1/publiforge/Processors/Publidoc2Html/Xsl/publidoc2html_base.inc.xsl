<?xml version="1.0" encoding="utf-8"?>
<!-- $Id: publidoc2html_base.inc.xsl 166825289936 2012/02/03 12:17:54 patrick $ -->
<xsl:stylesheet version="1.1" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

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
    <xsl:if test="head/title">
      <xsl:choose>
        <xsl:when test="count(ancestor::division)=0">
          <h2><xsl:apply-templates select="head/title"/></h2>
        </xsl:when>
        <xsl:when test="count(ancestor::division)=1">
          <h3><xsl:apply-templates select="head/title"/></h3>
        </xsl:when>
        <xsl:when test="count(ancestor::division)=2">
          <h4><xsl:apply-templates select="head/title"/></h4>
        </xsl:when>
        <xsl:otherwise>
          <h5><xsl:apply-templates select="head/title"/></h5>
        </xsl:otherwise>
      </xsl:choose>
      <xsl:if test="head/subtitle">
        <h6><xsl:apply-templates select="head/subtitle"/></h6>
      </xsl:if>
    </xsl:if>
    <xsl:apply-templates mode="onefile"/>
  </xsl:template>

  <xsl:template match="head|file|link" mode="onefile"/>

  <!--
      =========================================================================
      division mode maintoc & toc
      =========================================================================
  -->
  <xsl:template match="division" mode="maintoc">
    <li>
      <a href="{$fid}-div-{count(preceding::division)+1}.html">
        <xsl:choose>
          <xsl:when test="head/title">
            <xsl:apply-templates select="head/title"/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:value-of select="concat('Division ', count(preceding::topic)+1)"/>
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
      <xsl:choose>
        <xsl:when test="head/title">
          <xsl:apply-templates select="head/title"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="concat('Division ', count(preceding::division)+1)"/>
        </xsl:otherwise>
      </xsl:choose>
      <xsl:if test="head/subtitle"> — </xsl:if>
      <xsl:apply-templates select="head/subtitle"/>
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
            <xsl:value-of select="/*/*/head/title"/>
            <xsl-text> - </xsl-text>
          </xsl:if>
          <xsl:choose>
            <xsl:when test="head/title">
              <xsl:apply-templates select="head/title"/>
            </xsl:when>
            <xsl:otherwise>
              <xsl:value-of select="concat('Division ', count(preceding::division)+1)"/>
            </xsl:otherwise>
          </xsl:choose>
        </xsl:with-param>
        
        <xsl:with-param name="body">
          <body class="pdocDivision">
            <h1>
              <xsl:choose>
                <xsl:when test="head/title">
                  <xsl:apply-templates select="head/title"/>
                </xsl:when>
                <xsl:otherwise>
                  <xsl:value-of select="concat('Division ', count(preceding::division)+1)"/>
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
            <h2><xsl:apply-templates select="head/title"/></h2>
          </xsl:when>
          <xsl:when test="count(ancestor::division)=1">
            <h3><xsl:apply-templates select="head/title"/></h3>
          </xsl:when>
          <xsl:when test="count(ancestor::division)=2">
            <h4><xsl:apply-templates select="head/title"/></h4>
          </xsl:when>
          <xsl:otherwise>
            <h5><xsl:apply-templates select="head/title"/></h5>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:if>
      <xsl:if test="head/subtitle">
        <h6><xsl:apply-templates select="head/subtitle"/></h6>
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
      <a href="{$fid}-tpc-{count(preceding::topic)+1}.html">
        <xsl:choose>
          <xsl:when test="head/title">
            <xsl:apply-templates select="head/title"/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:value-of select="concat('Page ', count(preceding::topic)+1)"/>
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
          <div class="pdocNav col111">
            <div class="colFirst">
              <xsl:if test="count(preceding::topic)">
                <a href="{$fid}-tpc-{count(preceding::topic)}.html">
                  <img src="{$img_dir}go_previous.png" alt="Previous"/>
                </a>
              </xsl:if>
              <xsl:text> </xsl:text>
            </div>
            <div class="col">
              <a href="{$fid}.html">
                <img src="{$img_dir}go_up.png" alt="up"/>
              </a>
            </div>
            <div class="colLast">
              <xsl:if test="count(following::topic)">
                <a href="{$fid}-tpc-{count(preceding::topic)+2}.html">
                  <img src="{$img_dir}go_next.png" alt="Next"/>
                </a>
              </xsl:if>
              <xsl:text> </xsl:text>
            </div>
            <hr/>
          </div>

          <xsl:choose>
            <xsl:when test="head/title">
              <h1><xsl:apply-templates select="head/title"/></h1>
              <xsl:if test="head/subtitle">
                <h2><xsl:apply-templates select="head/subtitle"/></h2>
              </xsl:if>
            </xsl:when>
            <xsl:when test="not(preceding-sibling::topic) and parent::division/head/title">
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
    <xsl:if test=".//note">
      <div class="pdocNoteFooter">
        <xsl:apply-templates select=".//note" mode="footer"/>
      </div>
    </xsl:if>
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
              <xsl:value-of select="concat(substring-before(@name, '.xml'), '.html')"/>
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
          <xsl:when test="count(preceding-sibling::section)=0 and count(ancestor::section/preceding-sibling::section)=0">
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
    </div>
  </xsl:template>

  
  <!--
      *************************************************************************
                                      BLOCK LEVEL
      *************************************************************************
  -->
  <!--
      ========================================================================
      p
      ========================================================================
  -->
  <xsl:template match="p">
    <span class="pdocP"><xsl:apply-templates/><br/></span>
  </xsl:template>

  <xsl:template match="p" mode="text">
    <xsl:apply-templates mode="text"/><xsl:text> </xsl:text>
  </xsl:template>

  <!--
      ========================================================================
      speech
      ========================================================================
  -->
  <xsl:template match="speaker">
    <strong class="pdocSpeechSpeaker"><xsl:apply-templates/></strong>
    <xsl:if test="../stage">, </xsl:if>
  </xsl:template>

  <xsl:template match="stage">
    <span class="pdocSpeechStage"><em><xsl:apply-templates/></em></span>
  </xsl:template>

  <!--
      ========================================================================
      list
      ========================================================================
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
      ========================================================================
      blockquote
      ========================================================================
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
      ========================================================================
      media
      ========================================================================
  -->
  <xsl:template match="media">
    <xsl:if test="($img and image) or ($aud and audio)">
      <div class="pdocMedia">
        <xsl:if test="head/title">
          <div class="pdocMediaTitle"><xsl:apply-templates select="head/title"/></div>
        </xsl:if>
        <xsl:if test="head/subtitle">
          <div class="pdocMediaSubtitle"><xsl:apply-templates select="head/subtitle"/></div>
        </xsl:if>
        <xsl:apply-templates select="image|audio"/>
        <xsl:if test="caption">
          <div class="pdocMediaCaption">
            <xsl:apply-templates select="caption"/>
          </div>
        </xsl:if>
      </div>
    </xsl:if>
  </xsl:template>

  <xsl:template match="image">
    <div>
      <xsl:attribute name="class">
        <xsl:text>pdocImage</xsl:text>
        <xsl:if test="@type"> pdocImage-<xsl:value-of select="@type"/></xsl:if>
      </xsl:attribute>
      <xsl:choose>
        <xsl:when test="../link/@uri">
          <a href="{../link/@uri}">
            <img src="{$img_dir}{@id}{$img_ext}"><xsl:call-template name="alt"/></img>
          </a>
        </xsl:when>
        <xsl:when test="../link/@idref">
          <a href="#{../link/@idref}">
            <img src="{$img_dir}{@id}{$img_ext}"><xsl:call-template name="alt"/></img>
          </a>
        </xsl:when>
        <xsl:otherwise>
          <img src="{$img_dir}{@id}{$img_ext}"><xsl:call-template name="alt"/></img>
        </xsl:otherwise>
      </xsl:choose>
    </div>
    <xsl:if test="copyright">
      <div class="pdocMediaCopyright">
        <xsl:apply-templates select="copyright"/>
      </div>
    </xsl:if>
  </xsl:template>

  <xsl:template match="audio">
    <div>
      <xsl:attribute name="class">
        <xsl:text>pdocAudio</xsl:text>
        <xsl:if test="@type"> pdocAudio-<xsl:value-of select="@type"/></xsl:if>
      </xsl:attribute>
      <a href="{$aud_dir}{@id}{$aud_ext}">Son</a>
    </div>
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
      *************************************************************************
                                     INLINE LEVEL
      *************************************************************************
  -->
  <!--
      ========================================================================
      math
      ========================================================================
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
      ========================================================================
      number
      ========================================================================
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
      ========================================================================
      date
      ========================================================================
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
      ========================================================================
      note
      ========================================================================
  -->
  <xsl:template match="note">
    <a href="#n{count(preceding::note)+1}" id="nc{count(preceding::note)+1}"
       class="pdocNoteCall">
      <xsl:attribute name="title"><xsl:value-of select="normalize-space()"/></xsl:attribute>
      <sup>(<xsl:value-of select="count(preceding::note)+1"/>)</sup>
    </a>
  </xsl:template>

  <xsl:template match="note" mode="footer">
    <div>
      <a href="#nc{count(preceding::note)+1}" id="n{count(preceding::note)+1}">
        <xsl:value-of select="count(preceding::note)+1"/>
      </a>
      <xsl:text>. </xsl:text>
      <xsl:apply-templates/>
    </div>
  </xsl:template>

  <!--
      ========================================================================
      quote
      ========================================================================
  -->
  <xsl:template match="quote">
    <xsl:text>« </xsl:text>
    <em class="pdocQuote"><xsl:apply-templates/></em>
    <xsl:text> »</xsl:text>
  </xsl:template>

  <!--
      ========================================================================
      link, anchor
      ========================================================================
  -->
  <xsl:template match="link">
    <xsl:choose>
      <xsl:when test="@uri">
        <a href="{@uri}" class="pdocLink"><xsl:apply-templates/></a>
      </xsl:when>
      <xsl:when test="@idref">
        <a href="#{@idref}" class="pdocLink"><xsl:apply-templates/></a>
      </xsl:when>
      <xsl:otherwise>
        <span class="pdocLink"><xsl:apply-templates/></span>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="anchor"><a id="{@xml:id}"><xsl:text> </xsl:text></a></xsl:template>

  <!--
      ========================================================================
      Miscellaneous
      ========================================================================
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
    <xsl:document href="{$path}{$name}.html" method="xml"
                  encoding="utf-8" indent="yes"
                  doctype-public="-//W3C//DTD XHTML 1.1//EN"
                  doctype-system="http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
      <xsl:comment> Generated by PubliForge, $Date: 2012/02/03 12:17:54 $ </xsl:comment>
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
    <html xmlns="http://www.w3.org/1999/xhtml">
      <xsl:attribute name="xml:lang"><xsl:call-template name="lang"/></xsl:attribute>
      <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
        <meta http-equiv="Content-Language">
          <xsl:attribute name="content"><xsl:call-template name="lang"/></xsl:attribute>
        </meta>
        <title><xsl:value-of select="$title"/></title>
        <link rel="StyleSheet" href="Css/reset.css" type="text/css"/>
        <link rel="StyleSheet" href="Css/publidoc.css" type="text/css"/>
        <link rel="StyleSheet" href="Css/main.css" type="text/css"/>
      </head>
      <xsl:copy-of select="$body"/>
    </html>
  </xsl:template>

  <!--
      =========================================================================
      Template lang
      =========================================================================
  -->
  <xsl:template name="lang">
    <xsl:choose>
      <xsl:when test="/*/*/@xml:lang">
        <xsl:value-of select="/*/*/@xml:lang"/>
      </xsl:when>
      <xsl:otherwise>en</xsl:otherwise>
      </xsl:choose>
  </xsl:template>

</xsl:stylesheet>
