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

from Products.CMFCore.utils import getToolByName
import utilities
import messages
import re
__author__ = """ David Gonzalez Gonzalez -- dgg15@alu.ua.es"""

class GetRecord:

   def __init__(self):
      pass

   def getGetRecordXML(self,context,form):

      identifier = form["identifier"]
      search_result = utilities.searchRecord(context,identifier)

      if search_result != None:
         return messages.xmlGetRecord%(identifier,
                              search_result.Date().replace(' ','T')+'Z',
                              identifier,
                              search_result.Title(),
                              search_result.Description(),
                              search_result.Subject(),
                              search_result.Creator(),
                              search_result.Type(),
                              search_result.Format(),
                              search_result.Language(),
                              search_result.absolute_url())
      else:
         return messages.xmlErrorIllegal%(identifier)

