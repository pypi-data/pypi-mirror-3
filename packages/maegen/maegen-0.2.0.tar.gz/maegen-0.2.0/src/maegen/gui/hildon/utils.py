# -*- encoding: UTF-8 -*-

#    Maegen is a genealogical application for N900. Use it on the go
#    to store genealogical data including individuals and relational
#    informations. Maegen can be used to browse collected data on the
#    device but the main goal is its capabilitie to export the dtabase
#    in a GEDCOM file which can be imported into any desktop genealocial
#    application.
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
Created on Nov 16, 2011

@author: maemo
'''

import hildon
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

from maegen.common import version

version.getInstance().submitRevision("$Revision: 76 $")

def not_yet_implemented():
    show_banner_information("not yet implemented")

def show_note_information(mess):
       parent = hildon.WindowStack.get_default().peek()
       note = hildon.hildon_note_new_information(parent,mess)                 
   
       response = gtk.Dialog.run(note)

def show_banner_information(mess):
       parent = hildon.WindowStack.get_default().peek()
       banner= hildon.hildon_banner_show_information(parent,"", mess)
       banner.set_timeout(2000)  
       

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

def _default_exception_handler(gtk_sync = False):
        '''
        Do appropriate action when the core throw a Exception.
        Currently simply display a banner message.
        '''
        type, value,tb = sys.exc_info()             
        __default_exception_handler(type, value, tb, gtk_sync = gtk_sync)
                        
def __default_exception_handler(type, value, tb, gtk_sync = False):
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

       
def call_handled_method(method, *arg, **kwarg):
       '''
       This utility function catch error on a gentle way
       ''' 
       try:
            method(*arg, **kwarg)
       except :
            # this is an unkown exception
            _default_exception_handler()


class MaegenStackableWindow(hildon.StackableWindow):
    '''
    general design of any GUI of this app
    '''
    
    centerview = None;
    bottomButtons = None;
    
    def __init__(self, title="Maegen"):
        hildon.StackableWindow.__init__(self)
        
        self.program = hildon.Program.get_instance() 
        self.set_title(title)
   
        container = gtk.VBox();                
                  
        self.centerview = gtk.VBox() 
        
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

class AboutView(MaegenStackableWindow):
    '''
    This view show a fancy about dialog
    '''


    def init_center_view(self, centerview):
        
        pixbuf = gtk.gdk.pixbuf_new_from_file("maegen-logo.jpg")
        image = gtk.Image()
        image.set_from_pixbuf(pixbuf)
        centerview.add(image)
        
        centerview.add(gtk.Label("Maegen - " + version.getInstance().getVersion()))
        centerview.add(gtk.Label("Genealogical Application for N900"))
        centerview.add(gtk.Label("by Thierry Bressure - http://blog.maegen.bressure.net"))


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
Maegen is a genealogical application for N900. Use it
on the go to store genealogical data including
individuals and relational informations. Maegen can
be used to browse collected data on the device but
the main goal is its capabilitie to export the
database in a GEDCOM file which can be imported into
any desktop genealocial application.

Copyright (C) 2011  Thierry Bressure

This program is free software: you can redistribute
it and/or modify it under the terms of the GNU
General Public License as published by the Free
Software Foundation, either version 3 of the License,
or (at your option) any later version.

This program is distributed in the hope that it will
be useful, but WITHOUT ANY WARRANTY; without even the
implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public
License for more details.

You should have received a copy of the GNU General
Public License along with this program. If not, see
<http://www.gnu.org/licenses/>
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
        call_handled_method(open_browser_on,"http://blog.maegen.bressure.net")
    
    def on_site_clicked_event(self, widget, data):
        call_handled_method(open_browser_on,"http://maegen.bressure.net")
         
    def on_group_clicked_event(self, widget, data):
        call_handled_method(open_browser_on,"http://group.maegen.bressure.net")


class BugReportView(MaegenStackableWindow):
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
        MaegenStackableWindow.__init__(self, title="Bug reporting") 

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
        return MaegenStackableWindow.init_center_view(self, centerview)


    def init_bottom_button(self, bottomButtons):
        post = self.create_button("Post issue", None)
        post.connect("clicked", self.on_post_button_clicked, self)
        self.add_button(post)                     
        return MaegenStackableWindow.init_bottom_button(self, bottomButtons)

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
                    issues_client.client_login(username, password,"maegen", "code")
                    versionInstance = version.getInstance()
                    versionStr = versionInstance.getVersion()
                    revisionStr = versionInstance.getRevision()
                    labels = ['Type-Defect', 'Priority-High', 'Version-' + versionStr, 'Revision-' + revisionStr]
                    issues_client.add_issue("maegen", title, description, "tbressure", labels=labels)
                except:                    
                    show_banner_information("failed to send issue")
                    logging.exception("Failed to report the previous issue due to")
                else:
                    show_banner_information("issue sent")
            else:
                show_banner_information("bug report cancelled")
        finally:
            hildon.WindowStack.get_default().pop_1()


