# -*- encoding: UTF-8 -*-

#    Pyjama is a python project bootstraper for Maemo5 development
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
Created on Jan 6, 2012

@author: maemo
'''
import logging
import pickle
import os
import os.path

from model import *

from ..common import version 

version.getInstance().submitRevision("$Revision: 131 $")


'''
Facade functions
'''

def get_pyjama_storage_dir():
    '''
    Compute the application storage dir.
    This is an utility function to retrieve the directory where pyjama can
    store any file like settings or cached data.
    '''
    storage = os.path.expanduser("~")    
    storage = os.path.join(storage, ".pyjama")
    return storage



class pyjama(object):
    '''
    Main class of the Program. The GUI use this class like a Facade to any core functions.
    '''
    
    def __init__(self):
        self.connected = False
        self._ensure_pyjama_conf_store()        
        self.settings = None        
        self.load_settings()        
        self.apply_settings()

    def get_pyjama_settings_file(self):
        storage = get_pyjama_storage_dir()
        storage = os.path.join(storage, "settings.pickle")
        return storage

    def load_settings(self):
        '''
        load the saved settings
        '''
        self._ensure_pyjama_conf_store()
        storage = self.get_pyjama_settings_file()
        try:           
            file = open(storage,'rb')
            self.settings = pickle.load(file)
            file.close()
        except IOError, EOFError:
            logging.warning("failed to load the settings")
            self.settings  = Settings()
            
    
    def save_settings(self):
        '''
        save the current settings
        '''
        self._ensure_pyjama_conf_store()
        storage = self.get_pyjama_settings_file()
        try:           
            file = open(storage,'wb')
            pickle.dump(self.settings,file)
            file.close()
        except IOError:
            logging.warning("failed to save the settings")

    
    def apply_settings(self):        
       pass
                               
    
    def _ensure_pyjama_conf_store(self):
        storage = get_pyjama_storage_dir()
        if os.path.exists(storage):
            pass
        else:
            os.makedirs(storage)
            
    
    '''
    Facade method
    '''
        
    
    def get_settings(self):
        return self.settings
    
    
  
    def get_pyjama_storage_dir(self):
        '''
        Storage location of pyajama
        '''
        return get_pyjama_storage_dir()
            
    def generate(self, output,*argv, **kwarg):
        Project(*argv, **kwarg).generate(output)
        

