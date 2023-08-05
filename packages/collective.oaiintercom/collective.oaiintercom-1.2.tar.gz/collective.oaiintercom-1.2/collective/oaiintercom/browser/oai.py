# -*- coding: iso-8859-15 -*-

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

from zope.publisher.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
import datetime
import utilities
import messages
from identify import Identify
from listmetadataformats import ListMetadataFormats
from getrecord import GetRecord
from listsets import ListSets
from listrecords import ListRecords
import re
from listidentifiers import ListIdentifiers

__author__ = "David González González -- dgg15@alu.ua.es"

class OAIClass(BrowserView):
   """ This class implements an OAI view in Plone 3 filosophy """
   render = ViewPageTemplateFile('oai.pt')
   
   def __init__(self,context,request):
      self.context = context
      self.request = request

   def __call__(self):
      self.request.response.setHeader('Content-type', 'text/xml;; charset=utf-8')
      self.request.response.setHeader('charset',"UTF-8")
      return self.render()
   def getXML(self,request):
      
      response = """<responseDate>"""+utilities.formatedDate()+"""</responseDate>"""

      #no at the moment:
      if "resumptionToken" in self.request.keys():
         return "<responseDate>"+utilities.formatedDate()+"</responseDate>"+utilities.getRequestTag(self.context,self.request.form)+messages.badResumption

      #handling errors with stylish:
      error_params = utilities.errorHandler(self.request.form,self.context)
      if  error_params != None:
         return response + error_params
         
      # now we proccess the request:
      response = response + """ <request """
      for a in request.form.keys():
         if a != "-C": #preventing ? without params
            response = response + a+"=\""+request.form[a]+"\" "
      response = response+">"+self.context.portal_url()+"</request>"

      if request.form["verb"] == "Identify":
         response= response + self._getIdentify()
         return response

      if request.form["verb"] == "ListSets":
         response = response+self._getListSets()
         return response

      if request.form["verb"] == "ListMetadataFormats":
         response = response+self._getMetadataFormats()
         return response

      if request.form["verb"] == "GetRecord":
         response = response+self._getRecord(request)
         return response

      if request.form["verb"] == "ListRecords":
         response = response+self._getListRecords()
         return response

      if request.form["verb"] == "ListIdentifiers":
         response = response+self._getListIdentifiers()
         return response
      
      #in case of no cappable verb were found:
      return """<responseDate>"""+utilities.formatedDate()+"</responseDate>"+"<request>"+self.context.portal_url()+"</request>"+messages.badVerb
      

   def _getRecord(self,request):
      if len(request.form) == 3:
         records = GetRecord()
         return records.getGetRecordXML(self.context,request.form)
      else:
         return messages.badArgument

   def _getMetadataFormats(self):
      metadata_formats = ListMetadataFormats()
      return metadata_formats.getMetadataFormatsXML(self.request.form,self.context)

   def _getIdentify(self):
      identify = Identify()
      return identify.getIdentifyXML("Educommons OAI",self.context.portal_url(),self.context.email_from_address,"educommons.com")      
   
   def _getListSets(self):
      listsets = ListSets()
      return listsets.getListSetsXML(self.context)

   def _getListIdentifiers(self):
      listidentifiers = ListIdentifiers()
      # check dates
      from_date = ""
      until_date = ""

      if "from" in self.request.keys():
         from_date = self.request["form"]
      else:
         from_date = "2000-01-01"

      if "until" in self.request.keys():
         until_date = self.request["until"]
      else:
         until_date = "3000-01-01"

      if re.search("^[0-9]{4}-[0-9]{2}-[0-9]{2}$",from_date) and re.search("^[0-9]{4}-[0-9]{2}-[0-9]{2}$",until_date):
         return listidentifiers.getListIdentifiersXML(self.context,from_date,until_date)
      else:
         return messages.badArgument

   def _getListRecords(self):

         #no at the moment:
         if "resumptionToken" in self.request.keys():
            return "<responseDate>"+utilities.formatedDate()+"</responseDate>"+utilities.getRequestTag(self.context,self.request.form)+messages.badResumption

         listRecords = ListRecords() 
         from_date = ""
         until_date = ""

         if "from" in self.request.keys():
            from_date = self.request["from"]
         else:
            from_date = "2000-01-01"

         if "until" in self.request.keys():
            until_date = self.request["until"]
         else:
            until_date = "3000-01-01"
         if re.search("^[0-9]{4}-[0-9]{2}-[0-9]{2}$",from_date) and re.search("^[0-9]{4}-[0-9]{2}-[0-9]{2}$",until_date):
            return listRecords.getListRecordsXML(self.context,from_date,until_date)
         else:
            return messages.badArgument
