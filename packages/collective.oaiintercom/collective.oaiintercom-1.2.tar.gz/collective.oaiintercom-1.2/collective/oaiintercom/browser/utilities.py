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

import datetime
import messages
import re
from Products.CMFCore.utils import getToolByName

__author__ ="David González González -- dgg15@alu.ua.es"

""" This module has the utility functions. That's like a disaster drawer """ 

def formatedDate():
   """ Returns formated day """

   return datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')

def searchRecord(context,identifier):
      """ search for one record identified with identifier """

      portal_catalog = getToolByName(context, 'portal_catalog')
      query = {}
      query["id"] = identifier
      brains = portal_catalog.searchResults(**query)

      if len(brains)>0:
         return brains[0].getObject()
      else:
         return None

def searchRecords(context,date_start,date_end):
      """ search for records between dates """

      portal_catalog = getToolByName(context, 'portal_catalog')
      query = {}
      query['Date'] = {'query':[date_start, date_end],'range':'minmax'}
      brains = portal_catalog.searchResults(**query)

      if len(brains)>0:
         return brains
      else:
         return None

def searchSets(context):
      """ Search al sets in educommons plone site. Don't works with Plone """

      portal_catalog = getToolByName(context, 'portal_catalog')
      query = {}
      # it's only for educommons. Don't work with plone:
      query["Type"] = "Folder"
      brains = portal_catalog.searchResults(**query)
 
      if len(brains)>0:
         return brains
      else:
         return None

def errorHandler(form, context):
   """ this function manages the errors in the params. If there aren't errors return None. Else return xml with error """

   if "verb" not in form.keys():
      return messages.badVerb

   if form["verb"] == "Identify":
      test = testIdentify(form,context)
      if test != None:
         return test
   if form["verb"] == "ListSets":
      test = testListSets(form,context)
      if test!=None:
         return test
   if form["verb"] == "GetRecord":
      test = testGetRecord(form,context)
      if test!=None:
         return test
   if form["verb"] == "ListMetadataFormats":
      test = testListMetadataFormats(form, context)
      if test!=None:
         return test
   if form["verb"] == "ListRecords":
      test = testListRecords(form,context)
      if test!=None:
         return test
   if form["verb"] == "ListIdentifiers":
      test = testListIdentifiers(form,context)
      if test!=None:
         return test

   # if we survive... then no errors:
   return None

def testIdentify(form,context):
   """ This function test the Identify compilance """

   if len(form) != 1:   
      return messages.badArgument%(form["verb"],context.portal_url())
   else:
      return None

def testListSets(form,context):
   """ Testing list sets compilance """
  
   return testIdentify(form,context)
      
def testGetRecord(form,context):
   """ Test GetRecord compilance """   
   


   if len(form) != 3:
      return messages.badArgument%(form["verb"],context.portal_url())

   if "metadataPrefix" not in form.keys() or "identifier" not in form.keys():
      return messages.badArgument%(form["verb"],context.portal_url())

   if form["metadataPrefix"] != "oai_dc":
      return getRequestTag(context,form)+messages.cannotDiseminateFormat%(form["metadataPrefix"])

   identifier = form["identifier"]
   # Testing good arguments format:
   identifier = form["identifier"]
   p = re.compile("^[\w|-]+$")
   match = p.match(identifier)
   if match == None:
      return messages.badArgument%(form["verb"],context.portal_url())

   return None

def testListMetadataFormats(form, context):
   """ Test ListMetadataFormats compilance """

   if len(form) != 2 and len(form)!=1:
      return messages.badArgument%(form["verb"],context.portal_url())

   if len(form) == 2 and "identifier" not in form.keys():
      return messages.badArgument%(form["verb"],context.portal_url())

   if len(form) == 2:
      if searchRecord(context,form["identifier"]) == None:
         return getRequestTag(context,form)+messages.xmlErrorIllegal%(form["identifier"])

   return None

def testListRecords(form,context):
   from_date = "2000-01-01"
   until_date = "3000-01-01"

   if "from" in form.keys():
      from_date = form["from"]
   if "until" in form.keys():
      until_date = form["until"]
   if not re.search("^[0-9]{4}-[0-9]{2}-[0-9]{2}$",from_date) or not re.search("^[0-9]{4}-[0-9]{2}-[0-9]{2}$",until_date):
      return messages.badArgument%(form["verb"],context.portal_url())

   if "metadataPrefix" in form.keys():
      if form["metadataPrefix"] != "oai_dc":
         return messages.cannotDiseminateFormat%(form["metadataPrefix"])
   else:
      messages.badArgument%(form["verb"],context.portal_url())

   if len(form) == 4:
      if "from" in form.keys() and "until" in form.keys() and "metadataPrefix" in form.keys():
         return None
      else:
         return messages.badArgument%(form["verb"],context.portal_url())
   else:
      if len(form) == 3:
         if ("until" in form.keys() or "from" in form.keys()) and "metadataPrefix" in form.keys():
            return None
         else:
            return messages.badArgument%(form["verb"],context.portal_url())
   # fast patcher...
   if len(form) == 2:
         if "metadataPrefix" in form.keys():
            return None
   #in other case that not valid...
   return messages.badArgument%(form["verb"],context.portal_url())

def testListIdentifiers(form,context):
   if "resumptionToken" in form.keys():
      if(len(form)!=2):
         return messages.badArgument%(form["verb"],context.portal_url())
      else:
         return getRequestTag(context,form)+messages.badResumption # at the moment we don't support resumption token
   else:
      if len(form)==2:
         if "verb" not in form.keys() or "metadataPrefix" not in form.keys():
            return messages.badArgument%(form["verb"],context.portal_url())
         if len(list(form["metadataPrefix"])[0])>1:
            return messages.badArgument%(form["verb"],context.portal_url())
         if str(form["metadataPrefix"])!="oai_dc":
            return getRequestTag(context,form)+messages.cannotDiseminateFormat%(form["metadataPrefix"])
      else:
         if len(form)>2 and len(form)<=5:
            for a in form:
               if a not in ["from","until","set"]:
                  return messages.badArgument%(form["verb"],context.portal_url())
         else:
            return messages.badArgument%(form["verb"],context.portal_url())

   # we have exit cheking params
   return None
             

def getRequestTag(context,form):
   """ forms good request tag with all arguments. It isn't for bad argument """
   # preventing double arg pass:
   if "metadataPrefix" in form.keys():
      if form["metadataPrefix"] != "oai_dc":
         return "<request verb=\""+form["verb"]+"\">"+context.portal_url()+"</request>"

   response = """<request """
   for a in form.keys():
      if a != "-C": #preventing ? without params
         response = response + a+"=\""+str(form[a])+"\" "
   response = response+">"+context.portal_url()+"</request>"
   return response
      
