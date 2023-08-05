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
Created on Oct 14, 2011

@author: maemo
'''
import gtk
import hildon
import gobject
import logging
import sys, traceback
import os.path
import webbrowser
import logging
import threading
import time
import datetime
from Queue import *

#import gdata.projecthosting.client
#import gdata.projecthosting.data
#import gdata.gauth
#import gdata.client
#import gdata.data
#import atom.http_core
#import atom.core


import mock
from maegen.core import maegen

from maegen.common import version

version.getInstance().submitRevision("$Revision: 155 $")

gtk.gdk.threads_init()

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
       
def show_about_dialog(widget, data):
       '''
       Show an information dialog about the program
       '''
       window = AboutView()
       program = hildon.Program.get_instance()     
       program.add_window(window)
       window.show_all()


def _default_exception_handler(gtk_sync = False):
        '''
        Do appropriate action when the core throw a Exception.
        Currently simply display a banner message.
        '''
        type, value,tb = sys.exc_info()             
        self.__default_exception_handler(type, value, tb, gtk_sync = gtk_sync)
                        
def __default_exception_handler(type, value, tb, gtk_sync = False):
        logging.exception("!!! UNHANDLED EXCEPTION !!!")
        if gtk_sync :
            gtk.gdk.threads_enter()
        self.show_banner_information("An exception occured, please report the bug")
        window = BugReportView(type, value, tb, self.submit_issue)
        self.init_menu(window)
        self.program.add_window(window)
        window.show_all()
        if gtk_sync : 
            gtk.gdk.threads_leave()

       
def _call_handled_method(method, *arg):
       '''
       This utility function catch error on a gentle way
       ''' 
       try:
            method(*arg)
       except :
            # this is an unkown exception
            self._default_exception_handler()

      

class MaegenGui(object):
    '''
    This is the GUI of Maegen
    '''

    _last_folder = None

    def __init__(self, mocked=False):
        '''
        Create a new application GUI
        '''
        self.program = hildon.Program.get_instance()     
        if mocked :
           self.zcore = mock.Maegen()
        else:
           self.zcore = maegen.Maegen()
           
        self.__exception_fifo__ = Queue(0)
        self.exception_signal_handler_id = gobject.timeout_add(1000, self.receive_exception_signal)

        self.init_main_view()   

    def _set_default_folder_if_needed(self):
        if not self._last_folder:
            storage = os.path.expanduser("~")
            storage = os.path.join(storage, "MyDocs")
            storage = os.path.join(storage, ".documents")
            self._last_folder = storage

 


    def _default_exception_handler(self):
        '''
        Do appropriate action when the core throw a Exception.
        Currently simply display a banner message.
        '''
        type, value,tb = sys.exc_info() 
        self.__default_exception_handler(type, value, tb)
        
    def __default_exception_handler(self, type, value, tb):
        logging.exception("!!! UNHANDLED EXCEPTION !!!")      
        self.show_banner_information("An exception occured, please report the bug")     
        window = BugReportView(type, value, tb, self.submit_issue)
        self.init_menu(window)
        self.program.add_window(window)
        window.show_all()
    

    

    def send_exception_signal(self):
        '''
        Thread other than Gtk main, must call this method to post an exception
        '''
        self.__exception_fifo__.put(sys.exc_info())
        
    def receive_exception_signal(self):
        '''
        This method take an exception from the FIFO list of exception and
        display the corresponding GUI
        '''
        try:
            type, value, tb = self.__exception_fifo__.get_nowait()
            self.__default_exception_handler(type, value, tb)
        except Empty:
            pass
        return True
            

    def _call_handled_method(self, method, *arg):
        try:
            method(*arg)
        except :
            # this is an unkown exception
            self._default_exception_handler()




    def init_main_view(self):
        '''
        create a new window for the main view of the application
        '''
       
        # display a spashscreen
        window = SplashScreenView()       
        self.init_menu(window)
        self.program.add_window(window)       
        window.connect("destroy", self.quit_application, None)
        # This call show the window and also add the window to the stack
        window.show_all()

        # TODO do some stuff here                        

    def quit_application(self, widget, data):
        gobject.source_remove(self.exception_signal_handler_id)
        gtk.main_quit()
    
    def init_menu(self, window):
        '''
        create menu for all windows that will be used
        in this program
        '''
        menu = hildon.AppMenu()
                                                                                                                                                          
        newMenuBtn = hildon.GtkButton(gtk.HILDON_SIZE_AUTO);
        newMenuBtn.set_label("New");
        newMenuBtn.connect("clicked", self.show_new_dialog, None)
        menu.append(newMenuBtn)   
        
        openMenuBtn = hildon.GtkButton(gtk.HILDON_SIZE_AUTO);
        openMenuBtn.set_label("Open");
        openMenuBtn.connect("clicked", self.show_open_dialog, None)
        menu.append(openMenuBtn) 
        
        
        aboutMenuBtn = hildon.GtkButton(gtk.HILDON_SIZE_AUTO);
        aboutMenuBtn.set_label("About");
        aboutMenuBtn.connect("clicked", show_about_dialog, None)
        menu.append(aboutMenuBtn)

        
        menu.show_all()
        window.set_app_menu(menu)  
        

        
    

        

    
   
    


       
    def show_new_dialog(self, widget, data):
       '''
       Show dialog for new genealogical database
       '''
       parent = hildon.WindowStack.get_default().peek()
       fc = gobject.new(hildon.FileChooserDialog, title="New database", action=gtk.FILE_CHOOSER_ACTION_SAVE)
       fc.set_property('show-files',True)    
       fc.set_do_overwrite_confirmation(True)
       self._set_default_folder_if_needed()                   
       fc.set_current_folder(self._last_folder)
       if fc.run()==gtk.RESPONSE_OK: 
            filepath = fc.get_filename()    
            self._last_folder = fc.get_current_folder()              
            self.zcore.create_new_database(filepath)            
            window = DefaultView(self.zcore, filepath)        
            self.program.add_window(window)
            window.show_all()                     
       fc.destroy()

       
    def show_open_dialog(self, widget, data):
       '''
       Show dialog to select and open en existing genealogical database
       '''
       parent = hildon.WindowStack.get_default().peek()
       fc = gobject.new(hildon.FileChooserDialog, title="Choose a database", action=gtk.FILE_CHOOSER_ACTION_OPEN)
       fc.set_property('show-files',True)
       self._set_default_folder_if_needed()                   
       fc.set_current_folder(self._last_folder)
       if fc.run()==gtk.RESPONSE_OK: 
            filepath = fc.get_filename()
            self._last_folder = fc.get_current_folder()            
            fc.destroy()   
            self.zcore.load_database(filepath)                         
            window = DefaultView(self.zcore, filepath)        
            self.program.add_window(window)
            window.show_all()     
       else:                 
           fc.destroy()
              
    def submit_issue(self, title, description):
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
                    self.show_banner_information("failed to send issue")
                    logging.exception("Failed to report the previous issue due to")
                else:
                    self.show_banner_information("issue sent")
            else:
                self.show_banner_information("bug report cancelled")
        finally:
            hildon.WindowStack.get_default().pop_1()

    
    def run(self):
        # the splash screen  is displayed,now show the home screen in a fancy tansition               
        gtk.main()


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
      
      
class DefaultView(MaegenStackableWindow):
    '''
    This pane show somme statiscial information about the database
    and main action such as add a new individual and add a new family
    '''
    def __init__(self, zcore, database_filename):
        self.zcore = zcore       
        self.database_filename = database_filename
        self.individual_count_label = None
        self.family_count_label = None
        self.branche_count_label = None
        self.name_count_label = None
        MaegenStackableWindow.__init__(self, "Database content")
        
        # add app menu
        
        menu = hildon.AppMenu()
                                                                                                                                                          
        newMenuBtn = hildon.GtkButton(gtk.HILDON_SIZE_AUTO);
        newMenuBtn.set_label("Browse");
        newMenuBtn.connect("clicked", self.on_browse_menu_clicked, None)
        menu.append(newMenuBtn)   
        
        openMenuBtn = hildon.GtkButton(gtk.HILDON_SIZE_AUTO);
        openMenuBtn.set_label("Search");
        openMenuBtn.connect("clicked", self.on_search_menu_clicked, None)
        menu.append(openMenuBtn) 
        
        exportMenuBtn = hildon.GtkButton(gtk.HILDON_SIZE_AUTO);
        exportMenuBtn.set_label("Export");
        exportMenuBtn.connect("clicked", self.on_export_menu_clicked, None)
        menu.append(exportMenuBtn) 
        
        aboutMenuBtn = hildon.GtkButton(gtk.HILDON_SIZE_AUTO);
        aboutMenuBtn.set_label("About");
        aboutMenuBtn.connect("clicked", show_about_dialog, None)
        menu.append(aboutMenuBtn)
        
        menu.show_all()
        self.set_app_menu(menu)  
        
        # local variable
        self.selected_individual = None



    def refresh(self):
        self.individual_count_label.set_text(str(self.zcore.individuals_count()))
        self.family_count_label.set_text(str(self.zcore.families_count()))
        self.branche_count_label.set_text(str(self.zcore.branches_count()))
        self.name_count_label.set_text(str(self.zcore.names_count()))


    def on_export_menu_clicked(self, widget, data):
        dialog = gtk.Dialog()
        dialog.set_transient_for(self)
        dialog.set_title("Gedcom for database") 
        dialog.add_button("Save...", -1000)            
        gedcom = hildon.TextView()
        gedcom_source = self.zcore.export_to_gedcom()
        buffer = gtk.TextBuffer()
        buffer.set_text(gedcom_source)        
        gedcom.set_buffer(buffer)
        gedcom.set_property('editable', False)
        
        pannable_area = hildon.PannableArea()
        pannable_area.set_property('mov_mode',hildon.MOVEMENT_MODE_BOTH)
        pannable_area.set_property('size-request-policy', hildon.SIZE_REQUEST_CHILDREN)
        pannable_area.add_with_viewport(gedcom)
        dialog.vbox.add(pannable_area)
        dialog.show_all()
        response = dialog.run()
        if response == -1000:
            dialog.destroy()
            fc = gobject.new(hildon.FileChooserDialog, title="Enter gedcom file", action=gtk.FILE_CHOOSER_ACTION_SAVE)
            fc.set_property('show-files',True)    
            fc.set_do_overwrite_confirmation(True)                                        
            if fc.run()==gtk.RESPONSE_OK: 
                filepath = fc.get_filename()                                
                self.zcore.export_to_gedcom(filepath + ".ged")            
            fc.destroy()

        dialog.destroy()


    def on_browse_menu_clicked(self, widget, data):        
        '''
        Display a selector to view an individual
        '''
        selector = hildon.TouchSelector()
        model = gtk.ListStore(str, object)
        for indi in sorted(self.zcore.retrieve_all_individuals(), key=lambda indi : indi.name + indi.firstname):
            model.append([str(indi), indi])   
        selector.append_column(model, gtk.CellRendererText(),text=0)        
        selector.set_column_selection_mode(hildon.TOUCH_SELECTOR_SELECTION_MODE_SINGLE)
 

        dialog = hildon.PickerDialog(self) 
        dialog.set_transient_for(self) 
        dialog.set_title("Select an individual")
        dialog.set_done_label("View") 
        dialog.set_selector(selector)
        
        dialog.show_all()         
        self.selected_individual = None
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            model, iter = selector.get_selected(0)
            indi = model.get(iter,1)[0]        
            dialog.destroy()    
            window = IndividualView(self.zcore,indi, self.database_filename)
            self.program.add_window(window)
            window.show_all()
        else:
            dialog.destroy()        


           
        
    def on_search_menu_clicked(self, widget, data):
        not_yet_implemented()

    def init_center_view(self, centerview):
       line = gtk.HBox()
       line.pack_start(self.justifyLeft(gtk.Label("Individual")))
       self.individual_count_label = gtk.Label(self.zcore.individuals_count())
       line.pack_start(self.individual_count_label)
       centerview.pack_start(line)

       line = gtk.HBox()
       line.pack_start(self.justifyLeft(gtk.Label("Family")))
       self.family_count_label = gtk.Label(self.zcore.families_count())
       line.pack_start(self.family_count_label)       
       centerview.pack_start(line)
        
       line = gtk.HBox()
       line.pack_start(self.justifyLeft(gtk.Label("Branch")))
       self.branche_count_label = gtk.Label(self.zcore.branches_count())
       line.pack_start(self.branche_count_label)       
       centerview.pack_start(line)

       line = gtk.HBox()
       line.pack_start(self.justifyLeft(gtk.Label("Name")))
       self.name_count_label = gtk.Label(self.zcore.names_count())
       line.pack_start(self.name_count_label)       
       centerview.pack_start(line)

    
    
    def init_bottom_button(self, bottomButtons):
        add_indi_btn = self.create_button("Add Individual")
        add_indi_btn.connect("clicked", self.on_add_individual_clicked_event, None)
        self.add_button(add_indi_btn)
        
        add_fami_btn = self.create_button("Add Family")
        add_fami_btn.connect("clicked", self.on_add_family_clicked_event, None)
        self.add_button(add_fami_btn)
        
    def on_add_individual_clicked_event(self, widget, data):
        dialog = gtk.Dialog()
        dialog.set_transient_for(self)
        dialog.set_title("New individual")
        
        dialog.add_button("Create", gtk.RESPONSE_OK)
        firstname = hildon.Entry(gtk.HILDON_SIZE_AUTO)
        name = hildon.Entry(gtk.HILDON_SIZE_AUTO)
        nickname = hildon.Entry(gtk.HILDON_SIZE_AUTO)
        dialog.vbox.add(hildon.Caption(None,"Firstname",firstname))
        dialog.vbox.add(hildon.Caption(None,"Name",name))
        dialog.vbox.add(hildon.Caption(None,"Nickname",nickname))
        dialog.show_all()
        resu = dialog.run()
        if resu == gtk.RESPONSE_OK:            
            new_indi = self.zcore.create_new_individual(name.get_text(), firstname.get_text())
            self.zcore.save_database(self.database_filename)
            self.refresh()
            new_indi.nickname = nickname.get_text()
            dialog.destroy()
            window = IndividualView(self.zcore,new_indi, self.database_filename,edit_mode=self.zcore.settings.edit_new_individual)
            self.program.add_window(window)
            window.show_all()
        else:
            dialog.destroy()
        
    
    def on_add_family_clicked_event(self, widget, data):
        dialog = gtk.Dialog()
        dialog.set_transient_for(self)
        dialog.set_title("New Family")
        
        dialog.add_button("Create", gtk.RESPONSE_OK)
       
        selector = hildon.TouchSelector()        
        husband_model = gtk.ListStore(str, object)
        wife_model = gtk.ListStore(str, object)
        logging.debug("creating list for husband selection...")
        for indi in self.zcore.retrieve_all_individuals():
            if indi.gender in ["male", None] :
                    husband_model.append([str(indi), indi])
            elif indi.gender in ["female", None] :
                    wife_model.append([str(indi), indi])
            else:
                logging.warning("unexpected gender for " + str(parent))
                husband_model.append([str(indi), indi])
                wife_model.append([str(indi), indi])
                    
        selector.append_column(husband_model, gtk.CellRendererText(), text=0)
        selector.append_column(wife_model, gtk.CellRendererText(), text=0)
        selector.set_column_selection_mode(hildon.TOUCH_SELECTOR_SELECTION_MODE_SINGLE)
        dialog.vbox.pack_start(hildon.Caption(None, "Spouses" ,selector),expand=True)
        dialog.show_all()
        resu = dialog.run()
        if resu == gtk.RESPONSE_OK:            
            model, iter = selector.get_selected(0)
            husband = model.get(iter,1)[0]        
            model, iter = selector.get_selected(1)
            wife = model.get(iter,1)[0]        
            dialog.destroy()
            self.zcore.create_new_family(husband, wife)
            self.zcore.save_database(self.database_filename)
            self.refresh()
        else:
            dialog.destroy()


class IndividualView(MaegenStackableWindow):
    '''
    This pane show somme statistical information about the database
    and main action such as add a new individual and add a new family
    '''
    def __init__(self, zcore, individual, database_filename, edit_mode=False):
        self.zcore = zcore
        self.database_filename = database_filename
        self.individual = individual
        self.edit_mode = edit_mode
        self.edit_father = None
        self.edit_mother = None
        MaegenStackableWindow.__init__(self, str(individual))
        
                # add app menu
        
        menu = hildon.AppMenu()
                                                                                                                                                          
        if not self.edit_mode:
            editBtn = hildon.GtkButton(gtk.HILDON_SIZE_AUTO);
            editBtn.set_label("Edit");
            editBtn.connect("clicked", self._on_edit_menu_clicked, None)
            menu.append(editBtn)   
        

        
        aboutMenuBtn = hildon.GtkButton(gtk.HILDON_SIZE_AUTO);
        aboutMenuBtn.set_label("About");
        aboutMenuBtn.connect("clicked", show_about_dialog, None)
        menu.append(aboutMenuBtn)
        
        
        
        menu.show_all()
        self.set_app_menu(menu)  

    def pop_and_show_individual(self):
        hildon.WindowStack.get_default().pop_1()
        # open the clicked parent
        window = IndividualView(self.zcore, self.individual,self.database_filename, False)
        self.program.add_window(window)
        window.show_all()


    def _on_edit_menu_clicked(self, widget, data):
        # remove  the currentview
        hildon.WindowStack.get_default().pop_1()
        # open the clicked parent
        window = IndividualView(self.zcore,self.individual, self.database_filename, True)
        self.program.add_window(window)
        window.show_all()

    def init_bottom_button(self, bottomButtons):
        logging.debug("init_bottom_button for individualView...")
        if self.edit_mode: 
           logging.debug("in edit mode")
           save_btn = self.create_button("Save")
           save_btn.connect("clicked", self.on_save_clicked_event, None)
           self.add_button(save_btn)
        
           cancel_btn = self.create_button("Cancel")
           cancel_btn.connect("clicked", self.on_cancel_clicked_event, None)
           self.add_button(cancel_btn)
        else:
            logging.debug("not in edit mode, NO bottom button")
            
    def on_save_clicked_event(self, widget, data):
                            
        if self.edit_father and self.edit_mother:
            if self.father_enabled.get_active() and self.mother_enabled.get_active():                            
                self.zcore.set_parents(self.individual, self.edit_father, self.edit_mother)
            else:
                if not self.father_enabled.get_active():
                    self.zcore.remove_father(self.individual)
                if not self.mother_enabled.get_active():             
                    self.zcore.remove_mother(self.individual)
        else:    
            if self.edit_father:
                if self.father_enabled.get_active():                
                    self.zcore.set_father(self.individual,self.edit_father)
                else:                    
                    self.zcore.remove_father(self.individual)
            elif self.individual.father: 
                if not self.father_enabled.get_active():
                    self.zcore.remove_father(self.individual)
                
            if self.edit_mother:
                if self.mother_enabled.get_active():
                    self.zcore.set_mother(self.individual,self.edit_mother)
                else:
                    self.zcore.remove_mother(self.individual)
            elif self.individual.mother:
                if not self.mother_enabled.get_active():                 
                    self.zcore.remove_mother(self.individual)
            
        self.individual.name = self.edit_name.get_text()
        self.individual.firstname = self.edit_firstname.get_text()
        self.individual.nickname = self.edit_nickname.get_text()
        
        self.individual.occupation = self.edit_occupation.get_text()
        if self.birthdate_enable.get_active():
            y,m,d = self.edit_birthdate.get_date()
            self.individual.birthDate = datetime.date(y,m+1,d) 
        else:
            self.individual.birthDate = None
        if self.deathdate_enable.get_active():
            y,m,d = self.edit_deathdate.get_date()
            self.individual.deathDate = datetime.date(y,m+1,d)
        else:
            self.individual.deathDate = None
        
        model, iter = self.edit_gender_picker.get_selector().get_selected(0)
        self.individual.gender = model.get(iter,0)[0]      
        
        # after all job done, save the database
        self.zcore.save_database(self.database_filename)
        
        self.pop_and_show_individual()
        
    def on_cancel_clicked_event(self, widget, data):
        self.pop_and_show_individual()

    def _create_parent_pane(self, individual):
        logging.debug("creating parent pane for " + str(individual))
        if self.edit_mode:
            if self.edit_father:
                logging.debug("add a parent widget for edited father " + str(self.edit_father))
                self.parent_pane.pack_start(self._create_parent_widget(self.edit_father))
            elif individual.father:
                logging.debug("add a parent widget for current father " + str(individual.father))
                self.parent_pane.pack_start(self._create_parent_widget(individual.father))                
            else:
                logging.debug("add a button to set a father")
                add_father_btn = hildon.Button(gtk.HILDON_SIZE_AUTO_WIDTH | gtk.HILDON_SIZE_FINGER_HEIGHT, hildon.BUTTON_ARRANGEMENT_VERTICAL)
                add_father_btn.set_title("Add father")               
                add_father_btn.connect("clicked", self._open_dialog_to_select_parent, "father")
                self.parent_pane.pack_start(add_father_btn)
        elif individual.father:
                logging.debug("add a widget to navigate to current father " + str(individual.father))
                self.parent_pane.pack_start(self._create_parent_widget(individual.father))
        else:
            logging.debug("no widget for father because there is no father and not in edit mode")
            
                
            
        if self.edit_mode:
            if self.edit_mother:
                logging.debug("add a parent widget for edited mother " + str(self.edit_mother))
                self.parent_pane.pack_start(self._create_parent_widget(self.edit_mother))            
            elif individual.mother:
                logging.debug("add a parent widget for current mother " + str(individual.mother))
                self.parent_pane.pack_start(self._create_parent_widget(individual.mother))
            else:
                logging.debug("add a button to set a mother")                
                add_mother_btn = hildon.Button(gtk.HILDON_SIZE_AUTO_WIDTH | gtk.HILDON_SIZE_FINGER_HEIGHT, hildon.BUTTON_ARRANGEMENT_VERTICAL)
                add_mother_btn.set_title("Add mother")                
                add_mother_btn.connect("clicked", self._open_dialog_to_select_parent, "mother")
                self.parent_pane.pack_start(add_mother_btn)
        elif individual.mother:
            self.parent_pane.pack_start(self._create_parent_widget(individual.mother))
        else:
            logging.debug("no widget for mother becaue there is no mother and not in edit mode")

    def _open_dialog_to_select_parent(self, widget, parent):
        selector = hildon.TouchSelector()
        model = gtk.ListStore(str, object)
        logging.debug("creating list for parent selection...")
        for indi in self.zcore.retrieve_all_individuals():
            if parent == "father":
                if indi.gender in ["male", None] and not indi == self.individual:
                    model.append([str(indi), indi])
            elif parent == "mother":
                if indi.gender in ["female", None] and not indi == self.individual:
                    model.append([str(indi), indi])
            else:
                logging.error("unexpected parent parameter " + str(parent))
                    
        selector.append_column(model, gtk.CellRendererText(), text=0)
        selector.set_column_selection_mode(hildon.TOUCH_SELECTOR_SELECTION_MODE_SINGLE)
        def __enable_prent_checkbox(column , user_data):
            if parent == "father":
                self.father_enabled.set_active(True)    
            elif parent == "mother":
                self.mother_enabled.set_active(True)
            else:
                logging.error("unexpected parent parameter " + str(parent)) 
            
        selector.connect("changed", __enable_prent_checkbox)
        
        dialog = hildon.PickerDialog(self)
        dialog.set_transient_for(self)
        dialog.set_title("Select an individual")
        dialog.set_done_label("Set as parent")
        dialog.set_selector(selector)
        dialog.show_all()
        self.selected_individual = None
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            model, iter = selector.get_selected(0)
            indi = model.get(iter, 1)[0]
            dialog.destroy()
            if parent == "father":
                self.edit_father = indi
            elif parent == "mother":
                self.edit_mother = indi
            else:
                logging.error("unexpected parent parmaeter " + str(parent))
            for child in self.parent_pane.get_children():
                logging.debug("removing parent widget from parent pane...")
                self.parent_pane.remove(child)
            logging.debug("attemting to add new parent widget...")
            self._create_parent_pane(self.individual)
            self.parent_pane.show_all()
        else:
            dialog.destroy()


    def _create_gender_picker(self, individual):
        picker_button = hildon.PickerButton(gtk.HILDON_SIZE_AUTO, hildon.BUTTON_ARRANGEMENT_VERTICAL)
        picker_button.set_title("gender")
        selector = hildon.TouchSelector(text=True)
        picker_button.set_selector(selector)
        selector.append_text("unknown")
        selector.append_text("male")
        selector.append_text("female")
        if individual.gender == "male":
           picker_button.set_active(1)
        elif individual.gender == "female":
           picker_button.set_active(2)
        else:
           picker_button.set_active(0)
        
        return picker_button


    def _get_gender_image(self, individual):
        if individual.gender:
            if individual.gender == "male":
                pixbuf = gtk.gdk.pixbuf_new_from_file("male.png")
                image = gtk.Image()
                image.set_from_pixbuf(pixbuf)
            elif individual.gender == "female":
                pixbuf = gtk.gdk.pixbuf_new_from_file("female.png")
                image = gtk.Image()
                image.set_from_pixbuf(pixbuf)
            else:
                image = gtk.image_new_from_stock(gtk.STOCK_INFO, gtk.ICON_SIZE_BUTTON)
        else:
            image = gtk.image_new_from_stock(gtk.STOCK_INFO, gtk.ICON_SIZE_BUTTON)
        return image


    def _create_parent_widget(self, individual):
        widget = gtk.HBox()
        button = hildon.Button(gtk.HILDON_SIZE_AUTO_WIDTH | gtk.HILDON_SIZE_FINGER_HEIGHT, hildon.BUTTON_ARRANGEMENT_VERTICAL)
        # Set labels value
        datestr = ""
        if individual.birthDate:
            datestr += str(individual.birthDate.year)
        
        if individual.deathDate:
            datestr += "-" + str(individual.deathDate.year)
        
        button.set_text(str(individual), datestr)
        # Set image
        image = self._get_gender_image(individual)
          
            
        button.set_image(image)
        button.set_image_position(gtk.POS_RIGHT)
                                        
        button.connect("clicked", self._on_parent_clicked_event, individual)
        widget.pack_start(button)
        if self.edit_mode:
            
            if individual == self.individual.father and not self.edit_father:
                self.edit_father = None
            elif  individual == self.individual.mother and not self.edit_mother:
                self.edit_mother= None
            elif individual == self.edit_father:
                pass
            elif individual == self.edit_mother:
                pass
            else:
                logging.error("unexpected individual parameter " + str(individual))        
                   
            if individual == self.individual.father or individual == self.edit_father:                
                self.father_enabled = hildon.CheckButton(gtk.HILDON_SIZE_AUTO)
                self.father_enabled.set_label("enabled")
                self.father_enabled.set_active(True)
                widget.pack_start(self.father_enabled, expand=False)
            if individual == self.individual.mother or individual == self.edit_mother:                
                self.mother_enabled = hildon.CheckButton(gtk.HILDON_SIZE_AUTO)
                self.mother_enabled.set_label("enabled")
                self.mother_enabled.set_active(True)
                widget.pack_start(self.mother_enabled, expand=False)
               
        return widget
    
    
    def _create_partner_widget(self, individual):
        widget = gtk.HBox()
        button = hildon.Button(gtk.HILDON_SIZE_AUTO_WIDTH | gtk.HILDON_SIZE_FINGER_HEIGHT, hildon.BUTTON_ARRANGEMENT_VERTICAL)
        # Set labels value
        datestr = ""
        if individual.birthDate:
            datestr += str(individual.birthDate.year)
        
        if individual.deathDate:
            datestr += "-" + str(individual.deathDate.year)
        
        button.set_text(str(individual), datestr)
        # Set image
        image = self._get_gender_image(individual)
          
            
        button.set_image(image)
        button.set_image_position(gtk.POS_RIGHT)
                                        
        button.connect("clicked", self._on_partner_clicked_event, individual)
        widget.pack_start(button)

               
        return widget
    
    def _create_child_widget(self, individual):
        widget = gtk.HBox()
        button = hildon.Button(gtk.HILDON_SIZE_AUTO_WIDTH | gtk.HILDON_SIZE_FINGER_HEIGHT, hildon.BUTTON_ARRANGEMENT_VERTICAL)
        # Set labels value
        datestr = ""
        if individual.birthDate:
            datestr += str(individual.birthDate.year)
        
        if individual.deathDate:
            datestr += "-" + str(individual.deathDate.year)
        
        button.set_text(str(individual), datestr)
        # Set image
        image = self._get_gender_image(individual)
          
            
        button.set_image(image)
        button.set_image_position(gtk.POS_RIGHT)
                                        
        button.connect("clicked", self._on_child_clicked_event, individual)
        widget.pack_start(button)

               
        return widget
    
        
    def _on_child_clicked_event(self, widget, data):
            # remove  the currentview
            hildon.WindowStack.get_default().pop_1()
            # open the clicked parent
            window = IndividualView(self.zcore,data, self.database_filename)
            self.program.add_window(window)
            window.show_all()
    
    
    def _on_partner_clicked_event(self, widget, data):
            # remove  the currentview
            hildon.WindowStack.get_default().pop_1()
            # open the clicked parent
            window = IndividualView(self.zcore,data, self.database_filename)
            self.program.add_window(window)
            window.show_all()
    
    
    def _on_parent_clicked_event(self, widget, data):
        if self.edit_mode:
            # open a dialog an individual or create a new one
            if data == self.edit_father:
                self._open_dialog_to_select_parent(widget, "father")
            elif  data == self.edit_mother:                
                self._open_dialog_to_select_parent(widget, "mother")                
            elif data == self.individual.father and self.edit_father is None:                
                self._open_dialog_to_select_parent(widget, "father")
            elif data == self.individual.mother and self.edit_mother is None:
                self._open_dialog_to_select_parent(widget,"mother")
            else:
                logging.error("unexpected data attribute " + str(data))
           

        else:
            # remove  the currentview
            hildon.WindowStack.get_default().pop_1()
            # open the clicked parent
            window = IndividualView(self.zcore,data, self.database_filename)
            self.program.add_window(window)
            window.show_all()
    

    def create_header(self, individual):
        header = gtk.HBox()
        
        # Identification
        identification = gtk.VBox()
    
        # gender
        if self.edit_mode :
            self.edit_gender_picker = self._create_gender_picker(individual)
            identification.pack_start(self.edit_gender_picker, expand=False)
        else:
             identification.pack_start(self.justifyLeft(self._get_gender_image(individual)))
        # name
        if self.edit_mode:
            self.edit_name = hildon.Entry(gtk.HILDON_SIZE_AUTO)
            if self.individual.name:
                self.edit_name.set_text(self.individual.name)
            else:
                self.edit_name.set_placeholder("enter a name")
            self.edit_firstname = hildon.Entry(gtk.HILDON_SIZE_AUTO)
            if self.individual.firstname:
                self.edit_firstname.set_text(self.individual.firstname)
            else:
                self.edit_firstname.set_placeholder("enter the firstane")
            identification.pack_start(hildon.Caption(None,"Firstname",self.edit_firstname), expand=False)
            identification.pack_start(hildon.Caption(None,"Name",self.edit_name), expand=False) 
        else:            
            identification.pack_start(self.justifyLeft(gtk.Label(str(individual))))
        
        # nickname
        if self.edit_mode:
            self.edit_nickname = hildon.Entry(gtk.HILDON_SIZE_AUTO)
            if self.individual.nickname:
                self.edit_nickname.set_text(self.individual.nickname)
            else:
                self.edit_nickname.set_placeholder("enter a nickname")           
            identification.pack_start(hildon.Caption(None,"Nickname",self.edit_nickname), expand=False)
        else:
            if individual.nickname and individual.nickname != "":
                identification.pack_start(self.justifyLeft(gtk.Label("dit " + str(individual.nickname))))
        
        header.pack_start(identification)
        
        # Description        
        description = gtk.VBox()
        
        # occupation
        if self.edit_mode: 
            self.edit_occupation = hildon.Entry(gtk.HILDON_SIZE_AUTO)
            self.edit_occupation.set_placeholder(individual.occupation)
            description.pack_start(hildon.Caption(None,"Occupation",self.edit_occupation), expand=False)
        else:
            if individual.occupation and individual.occupation != "":            
                description.pack_start(self.justifyLeft(gtk.Label("occupation: " + individual.occupation.capitalize())))
        
        # birthdate
        if self.edit_mode:            
            hbox = gtk.HBox()
            self.edit_birthdate = hildon.hildon_date_button_new_with_year_range(gtk.HILDON_SIZE_AUTO_WIDTH | gtk.HILDON_SIZE_FINGER_HEIGHT, hildon.BUTTON_ARRANGEMENT_VERTICAL, min_year=1000, max_year=datetime.date.today().year)
            self.edit_birthdate.set_title("birth")            
            self.birthdate_enable = hildon.CheckButton(gtk.HILDON_SIZE_AUTO)
            self.birthdate_enable.set_label("enabled")
            if individual.birthDate:
                self.edit_birthdate.set_date(individual.birthDate.year, individual.birthDate.month-1, individual.birthDate.day)
                self.birthdate_enable.set_active(True)
            def __enable_birthdate_checkbox(column , user_data):
                self.birthdate_enable.set_active(True)
            self.edit_birthdate.get_selector().connect("changed", __enable_birthdate_checkbox)
            hbox.pack_start(self.edit_birthdate, expand=False)                                                                
            hbox.pack_start(self.birthdate_enable, expand=False)            
            description.pack_start(hbox , expand=False)

        else:
            if individual.birthDate :            
                description.pack_start(self.justifyLeft(gtk.Label("born on  " + str(individual.birthDate))))
        # deathdate
        if self.edit_mode:
            hbox = gtk.HBox()
            self.edit_deathdate = hildon.hildon_date_button_new_with_year_range(gtk.HILDON_SIZE_AUTO_WIDTH | gtk.HILDON_SIZE_FINGER_HEIGHT, hildon.BUTTON_ARRANGEMENT_VERTICAL, min_year=1000, max_year=datetime.date.today().year)
            self.edit_deathdate.set_title("dead")            
            self.deathdate_enable = hildon.CheckButton(gtk.HILDON_SIZE_AUTO)
            self.deathdate_enable.set_label("enabled")
            if individual.deathDate:
                self.edit_deathdate.set_date(individual.deathDate.year, individual.deathDate.month-1, individual.deathDate.day)
                self.deathdate_enable.set_active(True)
            def __enable_deathdate_checkbox(column , user_data):
                self.deathdate_enable.set_active(True)
            self.edit_deathdate.get_selector().connect("changed", __enable_deathdate_checkbox)                
            hbox.pack_start(self.edit_deathdate, expand=False)            
            hbox.pack_start(self.deathdate_enable, expand=False)                  
            description.pack_start(hbox , expand=False)

        else:
            if individual.deathDate :            
                description.pack_start(self.justifyLeft(gtk.Label("died on " + str(individual.deathDate))))
        # age od death
        if not self.edit_mode:
            if individual.birthDate and individual.deathDate:
                description.pack_start(self.justifyLeft(gtk.Label("Age of death " + str((individual.deathDate - individual.birthDate).days / 365) + " year(s) old")))
        
        
        header.pack_start(description)
        
        return header
    

    def create_parent_pane(self, individual):
        self.parent_pane = gtk.HBox()
        
        
        self._create_parent_pane(individual)        
        
        return self.parent_pane
    
    
    def create_families_pane(self, individual):
        families_pane = gtk.VBox()
        logging.info("looking for family of " + str(individual))
        for family in self.zcore.get_families_for(individual):
            logging.info("found a family")
            one_family_pane = gtk.HBox()
            # union with
            union = gtk.VBox()
            other = None
            if  individual == family.husband:
                other = family.wife
            else:
                other = family.husband            
            union.pack_start(self.justifyLeft(gtk.Label("with")))
            if other:                                
                union.pack_start(self._create_partner_widget(other),expand=False)
            else:
                union.pack_start(self.justifyLeft(gtk.Label("unknown partner")))            
            one_family_pane.add(union)
            # children
            children = gtk.VBox()
            children.pack_start(self.justifyLeft(gtk.Label("has " + str(len(family.children)) + " child(ren)")))
            for child in family.children:
                children.pack_start(self._create_child_widget(child),expand=False)
            
            one_family_pane.add(children)
            
            families_pane.pack_start(one_family_pane)
        
        
        return families_pane
  
  

    def init_center_view(self, centerview):
        frame = gtk.Frame("Identification")
        frame.add(self.create_header(self.individual))        
        centerview.pack_start(frame, expand=False,padding=5 )
        frame = gtk.Frame("Parents")
        frame.add(self.create_parent_pane(self.individual))
        centerview.pack_start(frame,expand=False, padding=5)
        frame = gtk.Frame("Marriages and children")
        frame.add(self.create_families_pane(self.individual))
        centerview.pack_start(frame, expand=False, padding=5)

    
    
        


        

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
         webbrowser.open_new_tab("http://blog.maegen.bressure.net");
    
    def on_site_clicked_event(self, widget, data):
         webbrowser.open_new_tab("http://maegen.bressure.net");
         
    def on_group_clicked_event(self, widget, data):
         webbrowser.open_new_tab("http://group.maegen.bressure.net");
             


class SplashScreenView(MaegenStackableWindow):
    '''
    This is the first view of the application e.g. the main view.  
    '''

    def init_center_view(self, centerview):
        pixbuf = gtk.gdk.pixbuf_new_from_file("maegen-logo.jpg")
        for i in range(1,4):
            hbox = gtk.HBox()
            for j in range(1,5):                
                image = gtk.Image()
                image.set_from_pixbuf(pixbuf)
                hbox.add(image)
            centerview.add(hbox)




       

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
    
    def __init__(self, type, value, traceback, submit_issue_callback):
        self.type = type
        self.value = value
        self.traceback = traceback
        self.submit_issue_callback = submit_issue_callback
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
        self.submit_issue_callback(subject, body)



