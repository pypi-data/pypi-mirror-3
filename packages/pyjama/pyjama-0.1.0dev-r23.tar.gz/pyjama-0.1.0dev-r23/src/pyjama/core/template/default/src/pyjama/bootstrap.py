${HEADER}
'''
Created on ${DATE_TIME}

@author: ${AUTHOR}
'''


from ${NAME}.core import facade

from optparse import OptionParser

import logging

from ${NAME}.common import version 


version.getInstance().submitRevision("$Revision: 4 $")


LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL}




def showGui():
    from ${NAME}.gui.hildon.${NAME}Gui import pyjamaGui 
    gui = pyjamaGui()
    gui.run()
    
def noGui():
    # directly use the facade
    # facade.xxxxx
    pass;
    
 

    
def run():
   versionManager = version.getInstance()
   usage = "%prog "
   str_version = "%prog " + versionManager.getVersion() + "(" + versionManager.getRevision() + ")"
   parser = OptionParser(usage=usage, version=str_version)
#
#   parser.add_option("-l","--login",action="store", dest="login", help="the login of the user without the @gmail")
#   parser.add_option("-p","--password",action="store", dest="password", help="the password for the given login")
#   parser.add_option("-d","--destination",action="store", dest="folder", help="the remote folder or album name")
#   parser.add_option("-r","--remove",action="store_true", dest="remove",  default=False, help="remove local file when uploaded")
#   parser.add_option("-f","--flatten",action="store_true", dest="flatten", default=False, help="subfolder are flattened to folder with name prefixed by given -d option value if any")
#   parser.add_option("-v","--verbose",action="store_true", dest="verbose", default=False, help="print verbose output of saving progress")
   parser.add_option("-g","--gui",action="store_true", dest="gui", default=False, help="show the gui")   
   parser.add_option("-l", "--log", action="store", type="string", dest="level_name", help="log level")
      
   (options, args) = parser.parse_args()
   
   level = LEVELS.get(options.level_name, logging.NOTSET)
   logging.basicConfig(level=level)

   if options.gui:   
       showGui()
   else:
       noGui()
    




if __name__ == '__main__':  
    run()
