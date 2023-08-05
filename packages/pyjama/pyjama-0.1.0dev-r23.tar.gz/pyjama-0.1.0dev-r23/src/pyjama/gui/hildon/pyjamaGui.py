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
Created on Oct 14, 2011

@author: maemo

'''
import gtk
import hildon
import logging
import os.path
import logging
import time
import datetime
import pango

import urllib



from pyjama.gui.gtk.widget import  *
from pyjama.gui.hildon.widget import *
from pyjama.gui.gtk.utils import fill_widget_with_logo, LOGO_PIXBUF
from pyjama.gui.hildon.utils import show_about_dialog, call_handled_method, not_yet_implemented, \
                                    PyjamaStackableWindow, ASYNC_EXCEPTION_HANDLER_INSTANCE, AsyncTask, \
                                    StopSignalException, show_banner_information, show_note_information
from pyjama.core import facade

from pyjama.common import version

version.getInstance().submitRevision("$Revision: 139 $")

from pyjama.gui.hildon.portrait import FremantleRotation


gtk.gdk.threads_init()


def show_new_window(window):
    program = hildon.Program.get_instance()
    program.add_window(window)
    window.show_all()


def show_album_list_view(facade):
        window = AlbumListView(facade)
        show_new_window(window)


def show_feed_list_view(facade):
        window = LastPictureView(facade)
        show_new_window(window)
      

class pyjamaGui(object):
    '''
    This is the GUI of gnatirac
    '''

    _last_folder = None

    def __init__(self):
        '''
        Create a new application GUI
        '''
        self.program = hildon.Program.get_instance()     
        self.facade = facade.pyjama()       
        ASYNC_EXCEPTION_HANDLER_INSTANCE.start_async_exception_handler()
        self.init_main_view()   




    def init_main_view(self):
        '''
        create a new window for the main view of the application
        '''
       
        # display a spashscreen
        window = SplashScreenView(self.facade)
        window.connect("destroy", self.quit_application, None)
        show_new_window(window)
        
        # autorotayion !!!
        FremantleRotation("Pyjama",main_window=window)       

        # TODO do some stuff here       
        if self.facade.connected:
            # Show album list
            show_album_list_view(self.facade)
                             

    def quit_application(self, widget, data):
        ASYNC_EXCEPTION_HANDLER_INSTANCE.stop_async_exception_handler()
        gtk.main_quit()
        

        
      
        
    def run(self):
        # the splash screen  is displayed,now show the home screen in a fancy tansition               
        gtk.main()


      

    
class SplashScreenView(PyjamaStackableWindow):
    '''
    This is the first view of the application e.g. the main view.  
    '''

    def __init__(self, facade):
        self.facade = facade
        PyjamaStackableWindow.__init__(self)

    def init_center_view(self, centerview):
        fill_widget_with_logo(centerview)

    


    def init_menu(self, menu):
        # add specific application menu here
        pass;
                                                                                                                                                          

 
        
        

                    
    