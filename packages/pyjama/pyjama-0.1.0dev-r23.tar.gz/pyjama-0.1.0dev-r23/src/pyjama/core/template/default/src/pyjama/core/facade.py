${HEADER}

'''
Created on ${DATE_TIME}

@author: ${AUTHOR}
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
            
