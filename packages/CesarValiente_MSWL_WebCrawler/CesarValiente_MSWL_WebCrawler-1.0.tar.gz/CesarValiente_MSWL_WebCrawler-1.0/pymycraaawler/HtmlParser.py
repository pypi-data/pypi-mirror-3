''' 
     Copyright 2011 Cesar Valiente Gordo
 
     This file is part of MSWL - Development and Tools WebCrawler exercise.

    This file is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This file is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this file.  If not, see <http://www.gnu.org/licenses/>.
'''

#Imports
from Log import Log
from Settings import Settings
from BeautifulSoup import BeautifulSoup as Soup


class HtmlParser:
    ''' Created on 06/11/2011
    
    @author: Cesar Valiente Gordo
    @mail: cesar.valiente@gmail.com
    
    This class is used to parser an entire html document and get the objects
    we want to use '''
    
    _CLASS_NAME = "HtmlParser"
            
        
    def parseLinks (self, rawCode, hostName):
        """ Parses the links of the used rawCode into a list """
        
        try:                            
            if (rawCode != None):
                soupCode = Soup(rawCode)
                
                #We get all links in raw mode (with http, without, ... all!)
                links = [link[Settings.HREF] for link 
                         in soupCode.findAll(Settings.A) if link.has_key(Settings.HREF)]                        
                            
                rawLinks = []                                                     
                #Adds the links to the list                                                                     
                for link in links:
                    rawLinks.append(link)                
                                                           
                #Parse the list with raw links to links with the correct host
                correctLinks = self.createCorrectLinks (links, hostName)
                
                return correctLinks
            
        except UnicodeEncodeError:
            return None
        except Exception:
            return None
                                                                                          
    def createCorrectLinks (self, rawLinks, hostName):
        """  Creates the correct links from the raw ones """
        
        try:
            if rawLinks != None and len(rawLinks)>0:
                correctLinks = []
                
                for link in rawLinks:                
                    if (str(link).find(Settings.HTTP) != 0) and (str(link).find(Settings.HTTPS) != 0):                    
                        link = hostName + str(link)
                                            
                    correctLinks.append(link)
                    
                return correctLinks
        except UnicodeEncodeError:
            return None
        except Exception:
            return None
                                                               
    
    
        


