<?xml version='1.0' encoding="utf-8"?>
<!-- $Id: publidoc2xhtml_i18n.inc.xsl 8f448be1af0e 2012/06/15 00:07:55 patrick $ -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:variable name="i18n_chapter">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Chapitre</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Capítulo</xsl:when>
      <xsl:otherwise>Chapter</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_part">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Partie</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Parte</xsl:when>
      <xsl:otherwise>Part</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_note">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Note</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Nota</xsl:when>
      <xsl:otherwise>Note</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_back">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Retour au texte</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Regresar al texto</xsl:when>
      <xsl:otherwise>Back to the text</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_noaudio">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Balise &lt;audio&gt; non supportée</xsl:when>
      <xsl:otherwise>&lt;audio&gt; tag not supported</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_novideo">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Balise &lt;video&gt; non supportée</xsl:when>
      <xsl:otherwise>&lt;video&gt; tag not supported</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

</xsl:stylesheet>
