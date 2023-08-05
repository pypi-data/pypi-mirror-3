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
import sys
import argparse
from Log import Log
 

class CheckArguments:
    ''' Created on 05/11/2011
    
    @author: Cesar Valiente Gordo
    @mail: cesar.valiente@gmail.com
    
    This class has all methods to use in the arguments parse funtionality '''
    
    _CLASS_NAME = "CheckArguments"
                                
    def checkArguments(self):
        """ This method checks the arguments which we have passed to the stdio """
        
        parser = argparse.ArgumentParser(description=  "Let's craaawl the Internet")                
        parser.add_argument("url", nargs=1, default=1, help="target URL")        
        parser.add_argument("-n", "--number-of-levels", type=int, default=1, 
                            help="how deep the craaawl will go")        
        args = parser.parse_args()
                     
        deep = args.__getattribute__("number_of_levels")                    
        url = args.__getattribute__("url")[0]         #Gets the 1st element (the url)
                                           
        #Checks the correct deep                                        
        if (deep <1):
            Log().d(self._CLASS_NAME, "You must provide a deep bigger than 0")
            sys.exit()                            
                   
        return (url, deep)                   
        
    
        
        
        
        
         
    
    
    
    


