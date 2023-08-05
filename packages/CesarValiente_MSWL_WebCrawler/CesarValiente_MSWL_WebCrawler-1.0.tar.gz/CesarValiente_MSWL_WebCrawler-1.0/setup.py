#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 25/09/2011

@author: Cesar Valiente Gordo
@contact: cesar.valiente@gmail.com
'''

from setuptools import setup, find_packages

setup (name = "CesarValiente_MSWL_WebCrawler",
    version = "1.0",
    packages = find_packages(),
    scripts = ['mycraaawler.py'],
    install_requires = ['BeautifulSoup'],
    package_data = {'pymycraaawler/':[''],},
    author = "Cesar Valiente Gordo",
    author_email = "cesar.valiente@gmail.com",
    description = "WebCrawler for the  Development & Tools subject of the M.Sc. on Free Software",
    license = "GNU GPLv3",
    keywords = "webcrawler",
    url = "https://github.com/CesarValiente/FLOSS",
    long_description = "WebCrawler for the  Development & Tools subject of the M.Sc. on Free Software",
    download_url = "http://pypi.python.org/pypi/MyCraaawler/1.0",)


#--- Remove this if you have problems to make the binary package and the registration ---#
""" Steps:
    In the mycraaawler.py directory (the one with the setup.py file, this file)
    >./setup.py register        (to register in pypi, if you don't have an account first create it with the option
                                            and after run again this command to register the app)
    >./setup.py sdist upload             (to create the source package and upload to pypi website)
    >./setup.py bdist upload            (to create the binary package and upload to pypi website)
    
"""                                        
