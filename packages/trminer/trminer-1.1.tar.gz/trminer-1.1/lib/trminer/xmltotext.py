import re
from lxml import etree

def XML_to_text(filepath, textfilepath):
    """
    Convert an xml file into plain text.
    
    Arguments:
    filepath -- the xml file path
    textfilepath -- the target text file path
    """
    f = open(filepath).read()
    #f = re.sub("(<.*?>)", " ", f)
    #f = re.sub("\s+", " ", f)
    
    xslt = etree.XML("""
    <xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    <xsl:output method="text"/>
    <xsl:template match="text()" />
    
    <xsl:template match="body//p">
        <xsl:apply-templates/>
        <xsl:text><![CDATA[ ]]></xsl:text>
    </xsl:template>
    
    <xsl:template match="body//p//text()[not(ancestor::fig) and not(ancestor::table-wrap)]">
        <xsl:value-of select="."/>
        <xsl:apply-templates/>
    </xsl:template>
    
    </xsl:stylesheet>
    """)
    transform = etree.XSLT(xslt)
    doc = etree.XML(f, base_url="/home2/koester/projects/trminer/adhesome")
    result_tree = transform(doc)
    
    open(textfilepath, "w").write(str(result_tree))
