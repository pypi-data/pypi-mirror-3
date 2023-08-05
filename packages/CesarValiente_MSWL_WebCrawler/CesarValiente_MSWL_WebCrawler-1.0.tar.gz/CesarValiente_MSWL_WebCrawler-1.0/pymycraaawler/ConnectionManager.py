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


from Settings import Settings
import urllib2
from urlparse import urlparse

class ConnectionManager:
    ''' Created on 05/11/2011
    
    @author: Cesar Valiente Gordo
    @mail: cesar.valiente@gmail.com
    
    This class has all methods to use in the connection with servers and urls '''
    
    #Timeout to use un the remote file reading (in seconds)
    _TIMEOUT = 5    
            
    def readRemoteUrl(self, url):
        """This function reads the website passed by parameter and sets the 
        rawCode parameter with the html code in brute """
                
        _opener = urllib2.build_opener()
        _opener.addheaders = [(Settings.USER_AGENT_TAG, Settings.USER_AGENT_CONTENT)]
        
        try:            
            rawCode = _opener.open(url, None, self._TIMEOUT).read()                  
            return rawCode      
            
        except BaseException:
            return None
        except Exception:            
            return None
            
            
    def parseUrl (self, url):
        """ Parses the complete url and returns itself parsed """    
        urlComponents =  urlparse(url)
        return urlComponents
            
        
    def getHostName (self, url):
        """ Parses the complete url and returns the hostName """        
        urlComponents = self.parseUrl(url)
        return urlComponents.netloc
 
                    
            
            
        
        
    

