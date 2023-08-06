<?xml version='1.0' encoding="utf-8"?>
<!-- $Id: publidoc2epub2_i18n.inc.xsl 69b9392e5aef 2012/06/14 21:10:54 patrick $ -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:variable name="i18n_title_page">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Page de titre</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Página de título</xsl:when>
      <xsl:otherwise>Title Page</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_copyright">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Copyright</xsl:when>
      <xsl:otherwise>Copyright</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_cover">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Couverture</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Cobertura</xsl:when>
      <xsl:otherwise>Cover</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_toc">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Sommaire</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Tabla de contenidos</xsl:when>
      <xsl:otherwise>Table of Contents</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_guide">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Guide</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Guía</xsl:when>
      <xsl:otherwise>Guide</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_notes">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Notes</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Notas</xsl:when>
      <xsl:otherwise>Notes</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_text">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Texte</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Texto</xsl:when>
      <xsl:otherwise>Text</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_Quiz">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Quiz</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Quiz</xsl:when>
      <xsl:otherwise>Quiz</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

</xsl:stylesheet>
