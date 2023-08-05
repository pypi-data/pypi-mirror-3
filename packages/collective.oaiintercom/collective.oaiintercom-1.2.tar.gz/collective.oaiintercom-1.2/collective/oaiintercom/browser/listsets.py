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
import messages
import utilities
from Products.CMFCore.utils import getToolByName

___author__ = """David Gonzalez Gonzalez - dgg15@alu.ua.es"""

class ListSets:
   def __init__(self):
      pass

   def getListSetsXML(self,context):
      result = utilities.searchSets(context)
      response = " "
      if result!=None:
         for a in result:
            message = messages.xmlListSets%(a.getObject().getId(),a.getObject().getId())
            response =  response +  message
         return "<ListSets>"+response+"</ListSets>"
      else:
         return "<error code=\"noSetHierarchy\">No sets.</error>"
