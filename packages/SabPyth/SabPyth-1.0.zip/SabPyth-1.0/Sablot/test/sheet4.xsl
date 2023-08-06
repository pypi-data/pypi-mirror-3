<xsl:stylesheet xmlns:xsl='http://www.w3.org/1999/XSL/Transform' version='1.0'>
<xsl:output encoding="unsupported-encoding"/>
  <xsl:template match='*'>
    *** <xsl:value-of select='//b'/>
    <xsl:apply-templates/>
  </xsl:template>
</xsl:stylesheet>
