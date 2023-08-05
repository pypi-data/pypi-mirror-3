# -*- encoding: UTF-8 -*-

#    Gnatirac is Picasa client for N900
#
#    Copyright (C) 2011  Thierry Bressure
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
'''
Created on Dec 29, 2011

@author: maemo
'''

from ..common import version 

version.getInstance().submitRevision("$Revision: 131 $")

class PyjamaCaptchaException(Exception):
    '''
    Login failure because google required a capcha
    '''            
    
    def __init__(self, token, url, doc_storage=None):
        self.captcha_token = token
        self.captcha_url = url
        self.doc_storage = doc_storage
        
    def get_token(self):
        return self.captcha_token
    
    def get_url(self):
        return self.captcha_url
    
    def get_storage(self):
        return self.doc_storage