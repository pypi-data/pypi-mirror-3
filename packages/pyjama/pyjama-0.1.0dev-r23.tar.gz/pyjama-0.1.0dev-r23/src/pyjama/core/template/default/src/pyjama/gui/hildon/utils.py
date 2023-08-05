${HEADER}

'''
Created on ${DATE_TIME}

@author: ${AUTHOR}
'''

import hildon
import gobject
import dbus
import gtk
import webbrowser
import sys, traceback
import logging

import gdata.projecthosting.client
import gdata.projecthosting.data
import gdata.gauth
import gdata.client
import gdata.data
import atom.http_core
import atom.core

import threading
from Queue import *

from ${NAME}.gui.gtk.utils import LOGO_PIXBUF

from ${NAME}.common import version

version.getInstance().submitRevision("$Revision: 131 $")


class Async_Exception_Handler():
    def __init__(self):
        self._exception_fifo = None
        self._exception_signal_handler_id = None

    def start_async_exception_handler(self):
        self._exception_fifo = Queue(0)
        self._exception_signal_handler_id = gobject.timeout_add(1000, self._receive_exception_signal) 
    

    def stop_async_exception_handler(self):
        gobject.source_remove(self._exception_signal_handler_id)

    def send_exception_signal(self):
        '''
        Thread other than Gtk main, must call this method to post an exception
        '''
        self._exception_fifo.put(sys.exc_info())

    def _receive_exception_signal(self):
        '''
        This method take an exception from the FIFO list of exception and
        display the corresponding GUI
        '''
        try:
            type, value, tb = self._exception_fifo.get_nowait()
            self._default_exception_handler(type, value, tb,gtk_sync=True)
        except Empty:
            pass
        return True 


    def default_exception_handler(self, gtk_sync = False):
        '''
        Do appropriate action when the core throw a Exception.
        Currently simply display a banner message.
        '''
        type, value,tb = sys.exc_info()             
        self._default_exception_handler(type, value, tb, gtk_sync = gtk_sync)
                        
    def _default_exception_handler(self, type, value, tb, gtk_sync = False):
        logging.exception("!!! UNHANDLED EXCEPTION !!!")
        if gtk_sync :
            gtk.gdk.threads_enter()
        show_banner_information("An exception occured, please report the bug")
        window = BugReportView(type, value, tb)
        program = hildon.Program.get_instance() 
        program.add_window(window)
        window.show_all()
        if gtk_sync : 
            gtk.gdk.threads_leave()
    
ASYNC_EXCEPTION_HANDLER_INSTANCE = Async_Exception_Handler()


def not_yet_implemented(gtk_sync = False):
    if gtk_sync :
            gtk.gdk.threads_enter()
    show_banner_information("not yet implemented")
    if gtk_sync : 
            gtk.gdk.threads_leave()

def show_note_information(mess, gtk_sync = False):
       if gtk_sync :
            gtk.gdk.threads_enter()
       parent = hildon.WindowStack.get_default().peek()
       note = hildon.hildon_note_new_information(parent,mess)                 
       response = gtk.Dialog.run(note)
       if gtk_sync :
            gtk.gdk.threads_leave()


def show_banner_information(mess, gtk_sync = False):
       if gtk_sync :
            gtk.gdk.threads_enter()   
       parent = hildon.WindowStack.get_default().peek()
       banner= hildon.hildon_banner_show_information(parent,"", mess)
       banner.set_timeout(2000)  
       if gtk_sync :
            gtk.gdk.threads_leave()   

       

def _show_about_dialog():
    window = AboutView()
    program = hildon.Program.get_instance()     
    program.add_window(window)
    window.show_all()

def show_about_dialog(widget, data):
       '''
       Show an information dialog about the program
       '''
       call_handled_method(_show_about_dialog)


def open_browser_on( url):
        bus = dbus.SystemBus()
        browser = dbus.Interface(bus.get_object('com.nokia.osso_browser', '/com/nokia/osso_browser/request'), 'com.nokia.osso_browser')
        browser.load_url(url)




        
      
       
def call_handled_method(method, *arg, **kwarg):
       '''
       This utility function catch error on a gentle way.
       Warning *only* GTK thread can use it.
       ''' 
       try:
            method(*arg, **kwarg)
       except :
            # this is an unkown exception
            ASYNC_EXCEPTION_HANDLER_INSTANCE.default_exception_handler()


class ${NAME_CAP}StackableWindow(hildon.StackableWindow):
    '''
    general design of any GUI of this app
    '''
    
    centerview = None;
    bottomButtons = None;
    
    def __init__(self, title="Pyjama", async_init=False, raise_stop_flag=None):
        '''
        Paremeter:
            - title : window title
            - async_init: True call the init_center_view in a separate thread. Default: False
            - raise_stop_flag: if async_init is True, défine the function to call when raise a stop request on the synchroneous thread
        '''
        hildon.StackableWindow.__init__(self)
        
        self.program = hildon.Program.get_instance() 
        self.set_title(title)
   
        self.menu = hildon.AppMenu()                
        self.init_menu(self.menu)
        
        aboutMenuBtn = hildon.GtkButton(gtk.HILDON_SIZE_AUTO);
        aboutMenuBtn.set_label("About");
        aboutMenuBtn.connect("clicked", show_about_dialog, None)
        self.menu.append(aboutMenuBtn)

        
        self.menu.show_all()
        self.set_app_menu(self.menu)  
        
   
        container = gtk.VBox();                
                  
        self.centerview = gtk.VBox() 
        
        if async_init:
            async_thread = AsyncTask(self, raise_stop_flag, self.init_center_view, centerview)
            async_thread.start()            
        else:
            self.init_center_view(self.centerview)
        
        pannable_area = hildon.PannableArea()
        pannable_area.set_property('mov_mode',hildon.MOVEMENT_MODE_BOTH)
        pannable_area.add_with_viewport(self.centerview)
        
        self.bottomButtons = gtk.HBox(homogeneous=True)
        
        self.init_bottom_button(self.bottomButtons)
        

        bottomAlign = gtk.Alignment(0.5,0,0,0)
        bottomAlign.add(self.bottomButtons)
        
        container.pack_start(pannable_area)
        container.pack_start(bottomAlign, expand=False)
        
        self.add(container)


    def init_menu(self, menu):
        '''
        This hook should be implemented by subclass to add window
        specific menu item
        '''
        pass;

    def init_center_view(self, centerview):
        '''
        This hook should be implemented by subclass to
        add widget in the centerview which is both instance
        and attribute variable for convenience
        '''
        pass;
    
    def init_bottom_button(self, bottomButtons):
        '''
        This hook should be implemented by subclass to
        add button in the bottom button which is both instance
        and attribute variable for convenience
        '''
        pass;

    def add_button(self, button):
        '''
        goodies to add a button to this view
        '''
        self.bottomButtons.pack_start(button,True,True,0)
    
    def create_button(self, name, value=None):
        '''
        goodies to create a button for this view
        ''' 
        return hildon.Button(gtk.HILDON_SIZE_THUMB_HEIGHT, hildon.BUTTON_ARRANGEMENT_HORIZONTAL, name, value)

    def justifyLeft(self, widget):
          leftAlign = gtk.Alignment(0,0.5,0,0)
          leftAlign.add(widget)
          return leftAlign
      
    def justifyRight(self, widget):
          leftAlign = gtk.Alignment(1,0.5,0,0)
          leftAlign.add(widget)
          return leftAlign

class AboutView(${NAME_CAP}StackableWindow):
    '''
    This view show a fancy about dialog
    '''


    def init_center_view(self, centerview):
        
        pixbuf = LOGO_PIXBUF
        image = gtk.Image()
        image.set_from_pixbuf(pixbuf)
        centerview.add(image)
        
        centerview.add(gtk.Label("${NAME_CAP} - " + version.getInstance().getVersion()))
        centerview.add(gtk.Label("${SUMMARY}"))
        centerview.add(gtk.Label("by ${AUTHOR} - ${PROJECT_URL}"))


    def init_bottom_button(self, bottomButtons):
        blogButton = self.create_button("Blog")
        blogButton.connect("clicked", self.on_blog_clicked_event, None)
        self.add_button(blogButton)
        
        siteButton = self.create_button("Site")
        siteButton.connect("clicked", self.on_site_clicked_event, None)
        self.add_button(siteButton)
        
        groupsiteButton = self.create_button("Groups")
        groupsiteButton.connect("clicked", self.on_group_clicked_event, None)
        self.add_button(groupsiteButton)
        
        licenceButton = self.create_button("Licence")
        licenceButton.connect("clicked", self.on_licence_clicked_event, None)
        self.add_button(licenceButton)

    def on_licence_clicked_event(self, widget, data):
        dialog = gtk.Dialog()
        dialog.set_transient_for(self)
        dialog.set_title("Copyright information")        
        dialog.add_button("Ok", gtk.RESPONSE_OK)
        gpl = hildon.TextView()
        gpl_licence = """
$DESCRIPTION

$COPYRIGHT

$LICENCE
"""
        buffer = gtk.TextBuffer()
        buffer.set_text(gpl_licence)        
        gpl.set_buffer(buffer)
        gpl.set_property('editable', False)
        
        pannable_area = hildon.PannableArea()
        pannable_area.set_property('mov_mode',hildon.MOVEMENT_MODE_BOTH)
        pannable_area.set_property('size-request-policy', hildon.SIZE_REQUEST_CHILDREN)
        pannable_area.add_with_viewport(gpl)
        dialog.vbox.add(pannable_area)
        dialog.show_all()
        dialog.run()
        dialog.destroy()

    def on_blog_clicked_event(self, widget, data):                                
        call_handled_method(open_browser_on,"${PROJECT_URL}")
    
    def on_site_clicked_event(self, widget, data):
        call_handled_method(open_browser_on,"${SITE_URL}")
         
    def on_group_clicked_event(self, widget, data):
        call_handled_method(open_browser_on,"${GROUP_URL}")


class BugReportView(${NAME_CAP}StackableWindow):
    '''
    This view show the bug and give the user the opportunity to report it
    '''
    type = None
    value = None
    traceback = None
    
    submit_issue_callback = None
    
    _body = None
    _subject = None
    
    def __init__(self, type, value, traceback):
        self.type = type
        self.value = value
        self.traceback = traceback       
        ${NAME_CAP}StackableWindow.__init__(self, title="Bug reporting") 

    def init_center_view(self, centerview):
       
        subjectLbl = gtk.Label("Subject")
        centerview.pack_start(self.justifyLeft(subjectLbl), False)
        self._subject = hildon.Entry(gtk.HILDON_SIZE_FULLSCREEN_WIDTH)
        self._subject.set_placeholder("enter a subject")
        self._subject.set_text(str(self.type) + " : " + str(self.value))
        centerview.pack_start(self._subject, False)
        contentLbl = gtk.Label("Content")
        centerview.pack_start(self.justifyLeft(contentLbl), False)
        self._body = hildon.TextView()
        self._body.set_placeholder("enter the message here")
        self._body.set_wrap_mode(gtk.WRAP_WORD)
        stacktrace = traceback.format_exception(self.type, self.value, self.traceback)
        buf = self._body.get_buffer()
        for line in stacktrace:
            end = buf.get_end_iter()
            buf.insert(end, line, len(line))
        centerview.add(self._body)
        return ${NAME_CAP}StackableWindow.init_center_view(self, centerview)


    def init_bottom_button(self, bottomButtons):
        post = self.create_button("Post issue", None)
        post.connect("clicked", self.on_post_button_clicked, self)
        self.add_button(post)                     
        return ${NAME_CAP}StackableWindow.init_bottom_button(self, bottomButtons)

    def on_post_button_clicked(self, widget, view):
        buffer = view._body.get_buffer()
        body = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter())
        subject =  view._subject.get_text()
        self._submit_issue(subject, body)


    def _submit_issue(self, title, description):
        # check credential
        try:
            parent = hildon.WindowStack.get_default().peek()
            dialog = hildon.LoginDialog(parent)
            dialog.set_message("Gmail account required")            
            response = dialog.run()
            username = dialog.get_username()
            password = dialog.get_password()
            dialog.destroy()
            if response == gtk.RESPONSE_OK:
                try:
                    issues_client = gdata.projecthosting.client.ProjectHostingClient()
                    issues_client.client_login(username, password,"${NAME}", "code")
                    versionInstance = version.getInstance()
                    versionStr = versionInstance.getVersion()
                    revisionStr = versionInstance.getRevision()
                    labels = ['Type-Defect', 'Priority-High', 'Version-' + versionStr, 'Revision-' + revisionStr]
                    issues_client.add_issue("${NAME}", title, description, "tbressure", labels=labels)
                except:                    
                    show_banner_information("failed to send issue")
                    logging.exception("Failed to report the previous issue due to")
                else:
                    show_banner_information("issue sent")
            else:
                show_banner_information("bug report cancelled")
        finally:
            hildon.WindowStack.get_default().pop_1()


class AsyncTask(threading.Thread):
    '''
    This is a gtk aware asynchroneous task.
    '''
    def __init__(self, window, stop_hook,  method, *argv, **kwarg):
            self.task_name = "${NAME_CAP}-AsyncTask"
            threading.Thread.__init__(self,name=self.task_name)
            self.method = method   
            self.argv = argv
            self.kwarg = kwarg
            self.window = window        
            self.stop_hook = stop_hook
            if self.window:
                window.connect("destroy", self._destroy_async_window,  None)

    def _destroy_async_window(self,  widget, data):
         self.send_stop_signal()
                     
        
    def run(self):            
            logging.debug("%s thread running...." % self.task_name)              
            if self.window:
                gtk.gdk.threads_enter()
                hildon.hildon_gtk_window_set_progress_indicator(self.window, 1)
                gtk.gdk.threads_leave()      
            try :                         
                self.cancellableAction()
            finally:
                if self.window:
                    gtk.gdk.threads_enter()
                    hildon.hildon_gtk_window_set_progress_indicator(self.window, 0)
                    gtk.gdk.threads_leave()                            
            logging.debug("%s thread finished" % self.task_name)

    def cancellableAction(self):
            try:
                self.method(*self.argv, **self.kwarg)
            except StopSignalException, sse:
                logging.info("%s aborted by software" % self.task_name)
            except Exception, e:
                logging.error("uncaught exception in %s \n%s" %(self.task_name,str(e)))
                # this thread is different fromgtk one so we must call this function
                # to post the current exception
                ASYNC_EXCEPTION_HANDLER_INSTANCE.send_exception_signal()
            else:
                logging.debug("%s terminated" % self.task_name)
            
    def send_stop_signal(self):
        if self.stop_hook:
            self.stop_hook()
        
class StopSignalException(Exception):
    pass
