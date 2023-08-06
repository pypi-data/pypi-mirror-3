<?xml version='1.0' encoding="utf-8"?>
<!-- $Id: publiquiz2xhtml_i18n.inc.xsl 52fe5fddd600 2012/04/30 09:04:24 patrick $ -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:variable name="i18n_help">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Aide</xsl:when>
      <xsl:otherwise>Help</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>
  <xsl:variable name="i18n_answer">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Réponse</xsl:when>
      <xsl:otherwise>Answer</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

</xsl:stylesheet>
