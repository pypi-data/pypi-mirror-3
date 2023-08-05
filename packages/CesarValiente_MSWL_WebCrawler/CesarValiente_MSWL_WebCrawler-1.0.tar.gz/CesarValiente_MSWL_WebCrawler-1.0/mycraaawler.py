#!/usr/bin/python
# -*- coding: utf-8 -*-

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
from pymycraaawler import HtmlParser
from pymycraaawler import Settings
from pymycraaawler import CheckArguments
from pymycraaawler import ConnectionManager
from pymycraaawler import Log
import sys

class MyCraaawler:
    ''' Created on 05/11/2011
    
    @author: Cesar Valiente Gordo
    @mail: cesar.valiente@gmail.com
    
    Main class of the project (Python script to launch the application and use the
    different modules created in the pymycraaawler folder '''
        
    _CLASS_NAME = "MyCraaawler"
    
    #Manager objects
    _connectionManager = None
    _htmlParser = None
    
    #Constants and log      
    _settings = None
    _log = None        
    
    #Deep object
    _deep = 1
            
    def __init__(self):
        """ Constructor """
        #Initializes the objects to use in settings and log
        self._settings = Settings.Settings()
        self._log = Log.Log()
                
        
        #Initialize the managers
        self._connectionManager = ConnectionManager.ConnectionManager()
        self._htmlParser = HtmlParser.HtmlParser()            
        
        #---------------------------------------------------------------#
        
        #Check the arguments
        checkArguments = CheckArguments.CheckArguments()
        (url,self._deep) = checkArguments.checkArguments()                            
        
        #Works with the url        
        rawCode = self._connectionManager.readRemoteUrl(url)        
        
        #checks the correct url
        if (rawCode == None):
            self._log.d(self._CLASS_NAME, "You must provide a valid url")
            sys.exit()
                
        #Processes raw html coded provided                                    
        links = self._htmlParser.parseLinks(rawCode, url)                                               
        
        #Starts to visit the links (the crawler functionality)
        self.visitLinks(links, 1)        
        
                                    
    def visitLinks (self, links, deep):
        """ Function which visits the links provided and got, so this is the heart
        of the spider (crawler) """        
        if links != None:
            for link in links:
                url = str(link)            
                if(deep < self._deep):                
                    self._log.d(self._CLASS_NAME, self.printDeep(deep) + " " + url.rstrip())
                    newLinks = self.getNewLinks(url)        
                    self.visitLinks(newLinks, deep+1)
                else:
                    self._log.d(self._CLASS_NAME, self.printDeep(deep) + " " + url.rstrip())
        
            
    def printDeep (self, deep):
        """ Creates the string with the '*' character serie appropriate to the deep """        
        deepLetter = ""
        for i in range(deep):
            deepLetter = deepLetter + "*"
            
        return deepLetter
        
                                                                                                            
    def getNewLinks (self, url):
        """ This function retrieves the new links of the website passed by param """        
        rawCode = self._connectionManager.readRemoteUrl(url)
        hostName = self._connectionManager.getHostName(url)
        newLinks = self._htmlParser.parseLinks(rawCode, hostName)
        
        return newLinks                                                    
                                   

def main():
    MyCraaawler()

if __name__ == '__main__':
    main()    
    
        
        