<?xml version='1.0' encoding="utf-8"?>
<!-- $Id: publidoc2html_cals.inc.xsl f482237c022c 2011/11/03 11:15:44 patrick $ -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <!--
      *************************************************************************
                                      BLOCK LEVEL
      *************************************************************************
  -->
  <!--
      ========================================================================
      table
      ========================================================================
  -->
  <xsl:template match="table">
    <xsl:if test="head/title">
      <div class="pdocTableTitle"><xsl:apply-templates select="head/title"/></div>
    </xsl:if>
    <xsl:if test="head/subtitle">
      <div class="pdocTableSubtitle"><xsl:apply-templates select="head/subtitle"/></div>
    </xsl:if>
    <xsl:apply-templates select="tgroup"/>
    <xsl:if test="caption">
      <div class="pdocTableCaption">
        <xsl:apply-templates select="caption"/>
      </div>
    </xsl:if>
  </xsl:template>

  <!--
      ========================================================================
      tgroup
      ========================================================================
  -->
  <xsl:template match="tgroup">
    <table class="pdocTable">
      <xsl:apply-templates select="thead"/>
      <xsl:apply-templates select="tbody"/>
      <!-- <xsl:apply-templates select="tfoot"/> -->
    </table>
  </xsl:template>

  <!--
      ========================================================================
      thead, tfoot, tbody
      ========================================================================
  -->
  <xsl:template match="thead|tfoot|tbody">
    <xsl:element name="{name(.)}">
      <xsl:if test="@valign">
        <xsl:attribute name="valign"><xsl:value-of select="@valign"/></xsl:attribute>
      </xsl:if>
      <xsl:apply-templates/>
    </xsl:element>
  </xsl:template>

  <!--
      ========================================================================
      row
      ========================================================================
  -->
  <xsl:template match="row">
    <tr>
      <xsl:if test="@valign">
        <xsl:attribute name="valign"><xsl:value-of select="@valign"/></xsl:attribute>
      </xsl:if>
      <xsl:apply-templates/>
    </tr>
  </xsl:template>
  
  <!--
      ========================================================================
      entry
      ========================================================================
  -->
  <xsl:template match="thead/row/entry|tfoot/row/entry">
    <xsl:call-template name="cell">
      <xsl:with-param name="tag">th</xsl:with-param>
    </xsl:call-template>
  </xsl:template>

  <xsl:template match="tbody/row/entry">
    <xsl:call-template name="cell"/>
  </xsl:template>

  <!--
      *************************************************************************
                                 CALLABLE TEMPLATES
      *************************************************************************
  -->
  <!--
      =========================================================================
      Template cell
      =========================================================================
  -->
  <xsl:template name="cell">
    <xsl:param name="tag">td</xsl:param>
    <xsl:element name="{$tag}">
      <xsl:apply-templates/>
    </xsl:element>
  </xsl:template>

</xsl:stylesheet>
