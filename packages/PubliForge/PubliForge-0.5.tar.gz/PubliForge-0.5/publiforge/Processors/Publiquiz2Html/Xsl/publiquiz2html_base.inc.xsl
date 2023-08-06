<?xml version="1.0" encoding="utf-8"?>
<!-- $Id: publiquiz2html_base.inc.xsl f4172bb1f2a8 2012/02/29 11:07:14 patrick $ -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <!--
      *************************************************************************
                                   COMPONENT LEVEL
      *************************************************************************
  -->
  <!--
      =========================================================================
      quiz mode maintoc & toc
      =========================================================================
  -->
  <xsl:template match="quiz" mode="maintoc">
    <xsl:apply-templates select="." mode="toc"/>
  </xsl:template>

  <xsl:template match="quiz" mode="toc">
    <li>
      <a href="{$fid}-quz-{count(preceding::quiz)+1}.html">
        <xsl:choose>
          <xsl:when test="head/title">
            <xsl:apply-templates select="head/title"/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:value-of select="concat('Page ', count(preceding::quiz)+1)"/>
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
      quiz mode file
      =========================================================================
  -->
  <xsl:template match="quiz" mode="file">
    <xsl:call-template name="html_file">
      <xsl:with-param name="name"
                      select="concat($fid, '-quz-', count(preceding::quiz)+1)"/>

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
            <xsl:value-of select="concat('Quiz ', count(preceding::quiz)+1)"/>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:with-param>

      <xsl:with-param name="body">
        <body class="pquizQuiz">
          <div class="pdocNav col111">
            <div class="colFirst">
              <xsl:if test="count(preceding::quiz)">
                <a href="{$fid}-quz-{count(preceding::quiz)}.html">
                  <img src="{$img_dir}go_previous.png" alt="Previous"/>
                </a>
              </xsl:if>
              <xsl:text> </xsl:text>
            </div>
            <div class="col">
              <a href="{$fid}.html">
                <img src="{$img_dir}go_up.png" alt="Up"/>
              </a>
            </div>
            <div class="colLast">
              <xsl:if test="count(following::quiz)">
                <a href="{$fid}-quz-{count(preceding::quiz)+2}.html">
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
            <xsl:when test="not(preceding-sibling::quiz) and parent::division/head/title">
              <h1><xsl:apply-templates select="parent::division/head/title"/></h1>
              <xsl:if test="parent::division/head/subtitle">
                <h2><xsl:apply-templates select="parent::division/head/subtitle"/></h2>
              </xsl:if>
            </xsl:when>
          </xsl:choose>
          <form action="#" method="post">
            <xsl:apply-templates select="." mode="corpus"/>
            <div class="pquizSubmit">
              <input type="submit" id="submit" class="pquizButton"/>
            </div>
          </form>
        </body>
      </xsl:with-param>
    </xsl:call-template>
  </xsl:template>

  <!--
      =========================================================================
      quiz mode corpus
      =========================================================================
  -->
  <xsl:template match="quiz" mode="corpus">
    <xsl:apply-templates select="instructions"/>
    <xsl:apply-templates select="choices-radio|choices-check|blanks-fill|blanks-select
                                 |point|matching|sort|production|composite"/>
    <xsl:apply-templates select="help|answer"/>
    <xsl:if test=".//note">
      <div class="pdocNoteFooter">
        <xsl:apply-templates select=".//note" mode="footer"/>
      </div>
    </xsl:if>
  </xsl:template>


  <!--
      *************************************************************************
                                   SECTION LEVEL
      *************************************************************************
  -->
  <!--
      ========================================================================
      instructions
      ========================================================================
  -->
  <xsl:template match="instructions">
    <div class="pquizInstructions">
      <xsl:if test="head/title">
        <div class="pquizInstructionsTitle">
          <xsl:apply-templates select="head/title"/>
        </div>
      </xsl:if>
      <xsl:if test="head/subtitle">
        <div class="pquizInstructionsSubtitle">
          <xsl:apply-templates select="head/subtitle"/>
        </div>
      </xsl:if>
      <xsl:apply-templates select="section|p|speech|list|blockquote|table|media"/>
    </div>
  </xsl:template>

  <!--
      ========================================================================
      choices-radio & choices-check
      ========================================================================
  -->
  <xsl:template match="choices-radio|choices-check">
    <xsl:variable name="quiz_id"><xsl:call-template name="quiz_id"/></xsl:variable>
    <div id="{$quiz_id}_engine">
      <xsl:attribute name="class">
        <xsl:value-of select="concat('pquizEngine ', name())"/>
        <xsl:if test="@shuffle='true'"> shuffle</xsl:if>
      </xsl:attribute>

      <div id="{$quiz_id}_correct" class="hidden">
        <xsl:for-each select="right">
          <xsl:value-of select="format-number(count(preceding-sibling::right
                                |preceding-sibling::wrong)+1, '00')"/>
          <xsl:text>x</xsl:text>
          <xsl:if test="count(following-sibling::right)">::</xsl:if>
        </xsl:for-each>
      </div>

      <ul class="pquizChoices">
        <xsl:for-each select="right|wrong">
          <li id="{concat($quiz_id, '_', format-number(
                  count(preceding-sibling::right|preceding-sibling::wrong)+1, '00'))}"
              class="pquizChoice">
            <input>
              <xsl:choose>
                <xsl:when test="name(..)='choices-radio'">
                  <xsl:attribute name="name"><xsl:value-of select="$quiz_id"/></xsl:attribute>
                  <xsl:attribute name="type">radio</xsl:attribute>
                </xsl:when>
                <xsl:when test="name(..)='choices-check'">
                  <xsl:attribute name="type">checkbox</xsl:attribute>
                </xsl:when>
              </xsl:choose>
            </input>
            <xsl:text> </xsl:text>
            <xsl:apply-templates/>
          </li>
        </xsl:for-each>
      </ul>
    </div>
  </xsl:template>

  <!--
      ========================================================================
      blanks
      ========================================================================
  -->
  <xsl:template match="blanks-fill|blanks-select">
    <xsl:variable name="quiz_id"><xsl:call-template name="quiz_id"/></xsl:variable>
    <div id="{$quiz_id}_engine">
      <xsl:attribute name="class">
        <xsl:value-of select="concat('pquizEngine ', name())"/>
        <xsl:if test="@strict='true'"> strict</xsl:if>
        <xsl:if test="@multiple='true'"> multiple</xsl:if>
      </xsl:attribute>
 
      <div id="{$quiz_id}_correct" class="hidden">
        <xsl:for-each select=".//blank">
          <xsl:call-template name="blank_num"/>
          <xsl:choose>
            <xsl:when test="s">
              <xsl:for-each select="s">
                <xsl:value-of select="normalize-space()"/>
                <xsl:if test="count(following-sibling::s)">|</xsl:if>
              </xsl:for-each>
            </xsl:when>
            <xsl:otherwise><xsl:value-of select="normalize-space()"/></xsl:otherwise>
          </xsl:choose>
          <xsl:call-template name="blank_separator"/>
        </xsl:for-each>
      </div>

      <xsl:if test="name()='blanks-select'">
        <div id="{$quiz_id}_items" class="pquizItems">
          <xsl:for-each select=".//blank|wrongs/wrong">
            <!-- <xsl:sort select="normalize-space()"/> -->
            <xsl:if test="not(ancestor::blanks-select[@multiple='true']) or
                          count(preceding::blank[normalize-space()=normalize-space(current())])
                          -count(ancestor::blanks-select/preceding::blank[normalize-space()=normalize-space(current())])=0">
              <span class="{$quiz_id} pquizItem">
                <xsl:value-of select="normalize-space()"/>
              </span>
            </xsl:if>
          </xsl:for-each>
        </div>
        <div class="clear"><xsl:text> </xsl:text></div>
      </xsl:if>

      <div class="pquizText">
        <xsl:apply-templates select="section|p|speech|list|blockquote|table|media"/>
      </div>
    </div>
  </xsl:template>

  <!--
      ========================================================================
      point
      ========================================================================
  -->
  <xsl:template match="point">
    <xsl:variable name="quiz_id"><xsl:call-template name="quiz_id"/></xsl:variable>
    <div id="{$quiz_id}_engine" >
      <xsl:attribute name="class">
        <xsl:text>pquizEngine point</xsl:text>
        <xsl:if test="@type">
          <xsl:value-of select="concat(' ', @type)"/>
        </xsl:if>
      </xsl:attribute>

      <div id="{$quiz_id}_correct" class="hidden">
        <xsl:for-each select=".//right">
          <xsl:call-template name="right_num"/>
          <xsl:text>x</xsl:text>
          <xsl:call-template name="right_separator"/>
        </xsl:for-each>
      </div>

      <div class="pquizText">
        <xsl:apply-templates/>
      </div>
    </div>
  </xsl:template>

  <!--
      ========================================================================
      matching
      ========================================================================
  -->
  <xsl:template match="matching">
    <xsl:variable name="quiz_id"><xsl:call-template name="quiz_id"/></xsl:variable>
    <div id="{$quiz_id}_engine" class="pquizEngine matching">
      <div id="{$quiz_id}_correct" class="hidden">
        <xsl:for-each select="match">
          <xsl:value-of select="format-number(count(preceding-sibling::match)+1, '00')"/>
          <xsl:value-of select="p[2]|section[2]"/>
          <xsl:if test="count(following-sibling::match)">::</xsl:if>
        </xsl:for-each>
      </div>

      <div id="{$quiz_id}_items" class="pquizItems">
        <xsl:for-each select="match">
          <xsl:sort select="normalize-space(p[2]|section[2])"/>
          <span class="{$quiz_id} pquizItem">
            <xsl:value-of select="normalize-space(p[2]|section[2])"/>
          </span>
        </xsl:for-each>
      </div>

      <table class="pquizMatching">
        <xsl:for-each select="match">
          <tr>
            <td>
              <xsl:apply-templates select="p[1]|section[1]"/>
            </td>
            <td id="{concat($quiz_id, '_',
                    format-number(count(preceding-sibling::match)+1, '00'))}"
                class="pquizDrop">
              .................
            </td>
          </tr>
        </xsl:for-each>
      </table>
    </div>
  </xsl:template>

  <!--
      ========================================================================
      sort
      ========================================================================
  -->
  <xsl:template match="sort">
    <xsl:variable name="quiz_id"><xsl:call-template name="quiz_id"/></xsl:variable>
    <div id="{$quiz_id}_engine">
      <xsl:attribute name="class">
        <xsl:text>pquizEngine sort</xsl:text>
        <xsl:if test="@shuffle='true'"> shuffle</xsl:if>
      </xsl:attribute>

      <div id="{$quiz_id}_correct" class="hidden">
        <xsl:for-each select="item">
          <xsl:value-of select="format-number(count(preceding-sibling::item)+1, '00')"/>
          <xsl:value-of select="normalize-space()"/>
          <xsl:if test="count(following-sibling::item)">::</xsl:if>
       </xsl:for-each>
      </div>

      <div id="{$quiz_id}_items" class="pquizItems">
        <xsl:for-each select="item">
          <xsl:sort select="@shuffle"/>
          <span class="{$quiz_id} pquizItem">
            <xsl:value-of select="normalize-space()"/>
          </span>
        </xsl:for-each>
      </div>
      <div class="clear"><xsl:text> </xsl:text></div>

      <div class="pquizText">
        <xsl:for-each select="item">
          <span
              id="{concat($quiz_id, '_',
                  format-number(count(preceding-sibling::item)+1, '00'))}"
              class="pquizDrop">.................</span>
          <xsl:if test="../comparison and count(following-sibling::item)">
            <xsl:text> </xsl:text>
            <xsl:apply-templates select="../comparison"/>
          </xsl:if>
          <xsl:text> </xsl:text>
        </xsl:for-each>
      </div>
    </div>
  </xsl:template>

  <!--
      ========================================================================
      production
      ========================================================================
  -->
  <xsl:template match="production">
    <textarea class="pquizProduction">
      <xsl:text> </xsl:text>
    </textarea>
  </xsl:template>


  <!--
      ========================================================================
      composite
      ========================================================================
  -->
  <xsl:template match="composite">
    <xsl:variable name="quiz_id"><xsl:call-template name="quiz_id"/></xsl:variable>
    <ol id="{$quiz_id}_engine" class="pquizEngines composite">
      <xsl:for-each select="subquiz">
        <li>
          <xsl:apply-templates select="instructions"/>
          <xsl:apply-templates select="choices-radio|choices-check|blanks-fill|blanks-select
                                       |point|matching|sort|production"/>
        </li>
      </xsl:for-each>
    </ol>
  </xsl:template>

  <!--
      ========================================================================
      help
      ========================================================================
  -->
  <xsl:template match="help">
    <xsl:variable name="quiz_id"><xsl:call-template name="quiz_id"/></xsl:variable>
    <div class="pquizHelp">
      <a href='#' id="{$quiz_id}_help-link">
        <xsl:attribute name="class">
          <xsl:text>pquizButton</xsl:text>
          <xsl:apply-templates select="link" mode="class"/>
        </xsl:attribute>
        <xsl:text>Aide</xsl:text>
      </a>
      <div id="{$quiz_id}_help-slot"><xsl:text> </xsl:text></div>
    </div>

    <xsl:call-template name="html_file">
      <xsl:with-param name="name" select="concat($quiz_id, '-hlp')"/>
      <xsl:with-param name="title">
        <xsl:value-of select="ancestor::quiz/head/title"/>
        <xsl:text> - Aide</xsl:text>
      </xsl:with-param>
      <xsl:with-param name="body">
        <body class="pquizHelp">
          <div>
            <xsl:apply-templates select="section|p|speech|list|blockquote|table|media"/>
          </div>
        </body>
      </xsl:with-param>
    </xsl:call-template>
  </xsl:template>

  <xsl:template match="link" mode="class">
    <xsl:if test="@uri">
      <xsl:text> </xsl:text>
      <xsl:value-of select="@uri"/>
    </xsl:if>
  </xsl:template>

  <xsl:template match="link" mode="include">
    <xsl:if test="@uri">
      <xsl:if test="//topic[@xml:id=current()/@uri]/head/title">
        <h1><xsl:apply-templates select="//topic[@xml:id=current()/@uri]/head/title"/></h1>
      </xsl:if>
      <xsl:apply-templates select="//topic[@xml:id=current()/@uri]"
                           mode="corpus"/>
    </xsl:if>
  </xsl:template>

  <!--
      ========================================================================
      answer
      ========================================================================
  -->
  <xsl:template match="answer">
    <xsl:variable name="quiz_id"><xsl:call-template name="quiz_id"/></xsl:variable>
    <div id="{$quiz_id}_answer-slot">
      <xsl:attribute name="class">
        <xsl:text>pquizAnswer</xsl:text>
        <xsl:apply-templates select="link" mode="class"/>
      </xsl:attribute>
      <xsl:text> </xsl:text>
    </div>

    <xsl:call-template name="html_file">
      <xsl:with-param name="name" select="concat($quiz_id, '-ans')"/>
      <xsl:with-param name="title">
        <xsl:value-of select="ancestor::quiz/head/title"/>
        <xsl:text> - Réponse</xsl:text>
      </xsl:with-param>
      <xsl:with-param name="body">
        <body class="pquizAnswer">
          <div>
            <xsl:apply-templates select="section|p|speech|list|blockquote|table|media"/>
          </div>
        </body>
      </xsl:with-param>
    </xsl:call-template>
  </xsl:template>


  <!--
      *************************************************************************
                                     INLINE LEVEL
      *************************************************************************
  -->
  <!--
      ========================================================================
      blank
      ========================================================================
  -->
  <xsl:template match="blank">
    <xsl:variable name="quiz_id"><xsl:call-template name="quiz_id"/></xsl:variable>
    <xsl:choose>
      <xsl:when test="ancestor::blanks-fill">
        <input type="text" class="pquizChoice">
          <xsl:attribute name="id">
            <xsl:value-of select="concat($quiz_id, '_')"/>
            <xsl:call-template name="blank_num"/>
          </xsl:attribute>
        </input>
      </xsl:when>
      <xsl:when test="ancestor::blanks-select">
        <span class="pquizDrop">
          <xsl:attribute name="id">
            <xsl:value-of select="concat($quiz_id, '_')"/>
            <xsl:call-template name="blank_num"/>
          </xsl:attribute>
          <xsl:text>.................</xsl:text>
        </span>
      </xsl:when>
    </xsl:choose>
  </xsl:template>

  <!--
      ========================================================================
      (point) right/wrong
      ========================================================================
  -->
  <xsl:template match="right|wrong">
    <xsl:variable name="quiz_id"><xsl:call-template name="quiz_id"/></xsl:variable>
    <span class="pquizChoice">
      <xsl:attribute name="id">
        <xsl:value-of select="concat($quiz_id, '_')"/>
        <xsl:call-template name="right_num"/>
      </xsl:attribute>
      <xsl:apply-templates/>
    </span>
  </xsl:template>


  <!--
      *************************************************************************
                                 CALLABLE TEMPLATES
      *************************************************************************
  -->
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
        <link rel="StyleSheet" href="Css/publiquiz.css" type="text/css"/>
        <link rel="StyleSheet" href="Css/main.css" type="text/css"/>
        <script src="Js/mootools.js" type="text/javascript"><xsl:text> </xsl:text></script>
        <script src="Js/publiquiz.js" type="text/javascript"><xsl:text> </xsl:text></script>
      </head>
      <xsl:copy-of select="$body"/>
    </html>
  </xsl:template>

  <!--
      =========================================================================
      Template quiz_id
      =========================================================================
  -->
  <xsl:template name="quiz_id">
    <xsl:choose>
      <xsl:when test="ancestor::composite">
        <xsl:value-of select="concat($fid, '-',
                              count(ancestor::composite/ancestor::quiz/preceding::quiz)+1,
                              '-', count(ancestor::subquiz/preceding-sibling::subquiz)+1)"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="concat($fid, '-', count(ancestor::quiz/preceding::quiz)+1)"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!--
      =========================================================================
      Template blank_num, blank_separator
      =========================================================================
  -->
  <xsl:template name="blank_num">
    <xsl:choose>
      <xsl:when test="ancestor::composite">
        <xsl:value-of select="format-number(count(preceding::blank)
                              -count(ancestor::subquiz/preceding::blank)+1, '00')"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="format-number(count(preceding::blank)
                              -count(ancestor::quiz/preceding::blank)+1, '00')"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template name="blank_separator">
    <xsl:choose>
      <xsl:when test="ancestor::composite">
        <xsl:if test="count(following::blank)-count(ancestor::subquiz/following::blank)">::</xsl:if>
      </xsl:when>
      <xsl:otherwise>
        <xsl:if test="count(following::blank)-count(ancestor::quiz/following::blank)">::</xsl:if>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!--
      =========================================================================
      Template right_num, right_separator
      =========================================================================
  -->
  <xsl:template name="right_num">
    <xsl:choose>
      <xsl:when test="ancestor::composite">
        <xsl:value-of select="format-number(
                              count(preceding::right|preceding::wrong)
                              -count(ancestor::subquiz/preceding::right
                              |ancestor::subquiz/preceding::wrong)+1, '00')"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="format-number(
                              count(preceding::right|preceding::wrong)
                              -count(ancestor::quiz/preceding::right
                              |ancestor::quiz/preceding::wrong)+1, '00')"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template name="right_separator">
    <xsl:choose>
      <xsl:when test="ancestor::composite">
        <xsl:if test="count(following::right)
                      -count(ancestor::subquiz/following::right)">::</xsl:if>
      </xsl:when>
      <xsl:otherwise>
        <xsl:if test="count(following::right)
                      -count(ancestor::quiz/following::right)">::</xsl:if>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

</xsl:stylesheet>
