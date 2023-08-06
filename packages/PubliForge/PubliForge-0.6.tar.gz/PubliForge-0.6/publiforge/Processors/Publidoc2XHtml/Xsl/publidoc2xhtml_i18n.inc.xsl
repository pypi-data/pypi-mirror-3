<?xml version='1.0' encoding="utf-8"?>
<!-- $Id: publidoc2xhtml_i18n.inc.xsl 59dc1f4773ee 2012/05/23 16:26:45 patrick $ -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:variable name="i18n_chapter">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Chapitre</xsl:when>
      <xsl:otherwise>Chapter</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_part">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Partie</xsl:when>
      <xsl:otherwise>Part</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_note">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Note</xsl:when>
      <xsl:otherwise>Note</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_back">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Retour au texte</xsl:when>
      <xsl:otherwise>Back to the text</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_noaudio">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Balise &lt;audio&gt; non supportée</xsl:when>
      <xsl:otherwise>&lt;audio&gt; tag not supported</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

</xsl:stylesheet>
