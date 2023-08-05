##################################################################################
#    Copyright (c) 2009 Massachusetts Institute of Technology, All rights reserved.
#                                                                                 
#    This program is free software; you can redistribute it and/or modify         
#    it under the terms of the GNU General Public License as published by         
#    the Free Software Foundation, version 2.                                     
#                                                                                 
#    This program is distributed in the hope that it will be useful,              
#    but WITHOUT ANY WARRANTY; without even the implied warranty of               
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                
#    GNU General Public License for more details.                                 
#                                                                                 
#    You should have received a copy of the GNU General Public License            
#    along with this program; if not, write to the Free Software                  
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA                                                                  
##################################################################################
# -*- coding: iso-8859-15 -*-
___author__ = """David Gonzalez Gonzalez - dgg15@alu.ua.es"""


badVerb = """<error code="badVerb">Illegal verb</error> """

badResumption = """<error code="badResumptionToken">Bad Resumption Token</error>"""

badArgument = """<request verb="%s">%s</request><error code="badArgument">
                The request includes illegal arguments, is missing required arguments, includes a repeated argument, or values for arguments have an illegal syntax.
</error> """

xmlIdentify = """<Identify>
<repositoryName>%s</repositoryName>
<baseURL>%s</baseURL>
<protocolVersion>2.0</protocolVersion>
<adminEmail>%s</adminEmail>
<earliestDatestamp>2000-01-01T00:00:00Z</earliestDatestamp>
<deletedRecord>no</deletedRecord>
<granularity>YYYY-MM-DDThh:mm:ssZ</granularity>
<compression>gzip</compression>
<compression>deflate</compression>
<description>
<oai-identifier xmlns="http://www.openarchives.org/OAI/2.0/oai-identifier" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai-identifier http://www.openarchives.org/OAI/2.0/oai-identifier.xsd">
<scheme>oai</scheme>
<repositoryIdentifier>%s</repositoryIdentifier>
<delimiter>:</delimiter>
<sampleIdentifier>oai:educommons.com:1</sampleIdentifier>
</oai-identifier>
</description>
</Identify>"""

xmlMetadataFormats = """<ListMetadataFormats>
<metadataFormat>
<metadataPrefix>oai_dc</metadataPrefix>
<schema>http://www.openarchives.org/OAI/2.0/oai_dc.xsd</schema>
<metadataNamespace>http://www.openarchives.org/OAI/2.0/oai_dc/</metadataNamespace>
</metadataFormat>
</ListMetadataFormats>"""


xmlGetRecord="""<GetRecord>
<record>
<header>
<identifier>%s</identifier>
<datestamp>%s</datestamp>
<setSpec>%s</setSpec>
</header>
<metadata>
<dc xmlns="http://www.openarchives.org/OAI/2.0/oai_dc/" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/ http://harvest.virtua.ua.es/metadata/xsd/dc/oai_dc.xsd">
<dc:title xml:lang="es-ES">%s</dc:title>
<dc:description xml:lang="es-ES">%s</dc:description>
<dc:subject xml:lang="es-ES">%s</dc:subject>
<dc:creator>%s</dc:creator>
<dc:type>%s</dc:type>
<dc:format>%s</dc:format>
<dc:language>%s</dc:language>
<dc:source>%s</dc:source>
</dc>
</metadata>
</record>
</GetRecord> """

xmlListSets = """<set>
<setSpec>%s</setSpec>
<setName>%s</setName>
</set>"""

xmlListRecordsHeader = """<header>
<identifier>%s</identifier>
<datestamp>%s</datestamp>
<setSpec>%s</setSpec>
</header>"""

xmlListRecordsBody= """<metadata>
<dc xmlns="http://www.openarchives.org/OAI/2.0/oai_dc/" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/ http://harvest.virtua.ua.es/metadata/xsd/dc/oai_dc.xsd">
<dc:subject xml:lang="es-ES">%s</dc:subject>
<dc:creator>%s</dc:creator>
<dc:type>%s</dc:type>
<dc:format>%s</dc:format>
<dc:language>%s</dc:language>
</dc>
</metadata>"""

xmlListIdentifiers = """<header>
<identifier>%s</identifier>
<datestamp>%s</datestamp>
<setSpec>%s</setSpec>
</header>
 """

cannotDiseminateFormat = """<error code="cannotDisseminateFormat">
"%s" is not supported by the item or by the repository
</error>"""

xmlErrorIllegal = """<error code="idDoesNotExist">
"%s" is unknown or illegal in this repository
</error>"""
