${HEADER}

'''
Created on ${DATE_TIME}

@author: ${AUTHOR}
'''

from ..common import version 

version.getInstance().submitRevision("$Revision: 131 $")

class ${NAME_CAP}CaptchaException(Exception):
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