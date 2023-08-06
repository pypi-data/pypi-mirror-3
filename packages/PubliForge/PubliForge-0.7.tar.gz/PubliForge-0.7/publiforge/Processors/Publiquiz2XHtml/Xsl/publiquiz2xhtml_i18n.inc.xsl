<?xml version='1.0' encoding="utf-8"?>
<!-- $Id: publiquiz2xhtml_i18n.inc.xsl 69b9392e5aef 2012/06/14 21:10:54 patrick $ -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:variable name="i18n_help">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Aide</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Ayuda</xsl:when>
      <xsl:otherwise>Help</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>
  
  <xsl:variable name="i18n_answer">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Réponse</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Respuesta</xsl:when>
      <xsl:otherwise>Answer</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

</xsl:stylesheet>
