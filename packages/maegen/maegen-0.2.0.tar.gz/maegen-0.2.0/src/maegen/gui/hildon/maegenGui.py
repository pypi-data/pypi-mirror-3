# -*- encoding: UTF-8 -*-

#    Maegen is a genealogical application for N900. Use it on the go
#    to store genealogical data including individuals and relational
#    informations. Maegen can be used to browse collected data on the
#    device but the main goal is its capabilitie to export the dtabase
#    in a GEDCOM file which can be imported into any desktop genealogical
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
import os.path
import logging
import threading
import time
import datetime
from Queue import *
import pango




import mock
from maegen.gui.gtk.widget import  *
from maegen.gui.gtk.utils import get_gender_image, get_gender_pixbuf, fill_widget_with_logo, get_life_date_str
from maegen.gui.hildon.utils import show_about_dialog, call_handled_method, not_yet_implemented, MaegenStackableWindow
from maegen.core import maegen

from maegen.common import version

version.getInstance().submitRevision("$Revision: 79 $")

#gtk.gdk.threads_init()

    

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
        self.init_main_view()   

    def _show_open_dialog(self, widget, data):
        parent = hildon.WindowStack.get_default().peek()
        fc = gobject.new(hildon.FileChooserDialog, title="Choose a database", action=gtk.FILE_CHOOSER_ACTION_OPEN)
        fc.set_property('show-files', True)
        self._set_default_folder_if_needed()
        fc.set_current_folder(self._last_folder)
        if fc.run() == gtk.RESPONSE_OK:
            filepath = fc.get_filename()
            self._last_folder = fc.get_current_folder()
            fc.destroy()
            self.zcore.load_database(filepath)
            window = DefaultView(self.zcore, filepath)
            self.program.add_window(window)
            window.show_all()
        else:
            fc.destroy()


    def _show_new_dialog(self, widget, data):
        parent = hildon.WindowStack.get_default().peek()        
        fc = gobject.new(hildon.FileChooserDialog, title="New database", action=gtk.FILE_CHOOSER_ACTION_SAVE)
        fc.set_property('show-files', True)
        fc.set_do_overwrite_confirmation(True)
        self._set_default_folder_if_needed()
        fc.set_current_folder(self._last_folder)
        if fc.run() == gtk.RESPONSE_OK:
            filepath = fc.get_filename()
            self._last_folder = fc.get_current_folder()
            self.zcore.create_new_database(filepath)
            window = DefaultView(self.zcore, filepath)
            self.program.add_window(window)
            window.show_all()
        
        fc.destroy()


    def _set_default_folder_if_needed(self):
        if not self._last_folder:
            storage = os.path.expanduser("~")
            storage = os.path.join(storage, "MyDocs")
            storage = os.path.join(storage, ".documents")
            self._last_folder = storage




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
       call_handled_method(self._show_new_dialog, widget, data)

       
    def show_open_dialog(self, widget, data):
       '''
       Show dialog to select and open en existing genealogical database
       '''
       call_handled_method(self._show_open_dialog,widget, data)
              
 
    
    def run(self):
        # the splash screen  is displayed,now show the home screen in a fancy tansition               
        gtk.main()


      

class IndividualListView(MaegenStackableWindow):
    '''
    This pane show individual list. This is a read view.
    '''
    
    def __init__(self, zcore, database_filename):
        
        self.zcore = zcore
        self.database_filename = database_filename
        MaegenStackableWindow.__init__(self, "Individuals list")
        
         # add app menu
        
        menu = hildon.AppMenu()
        
        aboutMenuBtn = hildon.GtkButton(gtk.HILDON_SIZE_AUTO);
        aboutMenuBtn.set_label("About");
        aboutMenuBtn.connect("clicked", show_about_dialog, None)
        menu.append(aboutMenuBtn)
        
        menu.show_all()
        self.set_app_menu(menu)

    def _on_row_activated(self, treeview, path, user_data):
        store = treeview.get_model()
        iter = store.get_iter(path)
        indi,  = store.get(iter, user_data)
        hildon.WindowStack.get_default().pop_1()
        window = IndividualView(self.zcore, indi, self.database_filename, False)
        self.program.add_window(window)
        window.show_all()




    def init_center_view(self, centerview):
        SEX_PICTURE_COLUMN_INDEX = 0
        FIRSTNAME_COLUMN_INDEX = 1
        NAME_COLUMN_INDEX = 2
        NICKNAME_COLUMN_INDEX = 3
        YEAR_BIRTH_DEATH_COLUMN_INDEX = 4
        OOCUPATION_COLUMN_INDEX = 5
        INDIVIDUAL_OBJECT_COLUMN_INDEX = 6
        self.model = gtk.ListStore(gtk.gdk.Pixbuf, str, str, str, str, str, object)
        for indi in self.zcore.retrieve_all_individuals():            
            sex_picture = get_gender_pixbuf(indi)
                                
            year_birth_death = get_life_date_str(indi)
                
            self.model.append([sex_picture, indi.firstname, indi.name.upper(), indi.nickname, year_birth_death, indi.occupation, indi])   
        
        self.view = gtk.TreeView(self.model)     
        self.view.set_headers_visible(True)           
        self.view.set_headers_clickable(True)
        
        column = gtk.TreeViewColumn("S")
        column_renderer = gtk.CellRendererPixbuf()
        column.pack_start(column_renderer)
        column.set_attributes(column_renderer, pixbuf=SEX_PICTURE_COLUMN_INDEX) 
        self.view.append_column(column)
        
        column = gtk.TreeViewColumn("firstname")
#        column.set_property("sizing", gtk.TREE_VIEW_COLUMN_FIXED)
#        column.set_property("fixed-width", 300)
        column_renderer = gtk.CellRendererText()
        column.pack_start(column_renderer)
        column.set_attributes(column_renderer, text=FIRSTNAME_COLUMN_INDEX) 
        self.view.append_column(column)
        
        column = gtk.TreeViewColumn("name")
#        column.set_property("sizing", gtk.TREE_VIEW_COLUMN_FIXED)
#        column.set_property("fixed-width", 300)
        column_renderer = gtk.CellRendererText()
        column.pack_start(column_renderer)
        column.set_attributes(column_renderer, text=NAME_COLUMN_INDEX) 
        self.view.append_column(column)
        
        column = gtk.TreeViewColumn("nick")
#        column.set_property("sizing", gtk.TREE_VIEW_COLUMN_FIXED)
#        column.set_property("fixed-width", 300)
        column_renderer = gtk.CellRendererText()
        column.pack_start(column_renderer)
        column.set_attributes(column_renderer, text=NICKNAME_COLUMN_INDEX) 
        self.view.append_column(column)
        
        column = gtk.TreeViewColumn("birth-death")
#        column.set_property("sizing", gtk.TREE_VIEW_COLUMN_FIXED)
#        column.set_property("fixed-width", 300)
        column_renderer = gtk.CellRendererText()
        column.pack_start(column_renderer)
        column.set_attributes(column_renderer, text=YEAR_BIRTH_DEATH_COLUMN_INDEX) 
        self.view.append_column(column)

        column = gtk.TreeViewColumn("occupation")
#        column.set_property("sizing", gtk.TREE_VIEW_COLUMN_FIXED)
#        column.set_property("fixed-width", 300)
        column_renderer = gtk.CellRendererText()
        column.pack_start(column_renderer)
        column.set_attributes(column_renderer, text=OOCUPATION_COLUMN_INDEX) 
        self.view.append_column(column)
                

        self.view.connect("row-activated", self.on_row_activated, INDIVIDUAL_OBJECT_COLUMN_INDEX)
        

        
        
        centerview.add(self.view)
        

    def on_row_activated(self,  treeview, path, view_column,  user_data):
        call_handled_method(self._on_row_activated,treeview, path, user_data)


class BranchListView(MaegenStackableWindow):
    '''
    This pane show branches. This is a read view.
    '''
    
    def __init__(self, zcore, database_filename):
        
        self.zcore = zcore
        self.database_filename = database_filename
        MaegenStackableWindow.__init__(self, "Branch list")
        
         # add app menu
        
        menu = hildon.AppMenu()
        
        aboutMenuBtn = hildon.GtkButton(gtk.HILDON_SIZE_AUTO);
        aboutMenuBtn.set_label("About");
        aboutMenuBtn.connect("clicked", show_about_dialog, None)
        menu.append(aboutMenuBtn)
        
        menu.show_all()
        self.set_app_menu(menu)

    def _on_row_activated(self, treeview, path, user_data):
        store = treeview.get_model()
        iter = store.get_iter(path)
        indi,  = store.get(iter, user_data)
        hildon.WindowStack.get_default().pop_1()
        window = IndividualView(self.zcore, indi, self.database_filename, False)
        self.program.add_window(window)
        window.show_all()


    def init_center_view(self, centerview):
        LEVEL_COLUMN_INDEX = 0
        SEX_PICTURE_COLUMN_INDEX = 1
        FIRSTNAME_COLUMN_INDEX = 2
        NAME_COLUMN_INDEX = 3
        NICKNAME_COLUMN_INDEX = 4
        YEAR_BIRTH_DEATH_COLUMN_INDEX = 5
        OOCUPATION_COLUMN_INDEX = 6
        INDIVIDUAL_OBJECT_COLUMN_INDEX = 7
        self.model = gtk.TreeStore(str, gtk.gdk.Pixbuf, str, str, str, str, str, object)
        for indi in self.zcore.retrieve_branches():
            
            self._add_indivdual_in_tree(None, indi, level=1)
            # TODO add children
               
        
        self.view = gtk.TreeView(self.model)     
        self.view.set_headers_visible(True)           
        self.view.set_headers_clickable(True)
        
        column = gtk.TreeViewColumn("Level")
        column_renderer = gtk.CellRendererText()
        column.pack_start(column_renderer)
        column.set_attributes(column_renderer, text=LEVEL_COLUMN_INDEX) 
        self.view.append_column(column) 
        
        
        column = gtk.TreeViewColumn("S")
        column_renderer = gtk.CellRendererPixbuf()
        column.pack_start(column_renderer)
        column.set_attributes(column_renderer, pixbuf=SEX_PICTURE_COLUMN_INDEX) 
        self.view.append_column(column)    
        
        column = gtk.TreeViewColumn("firstname")
#        column.set_property("sizing", gtk.TREE_VIEW_COLUMN_FIXED)
#        column.set_property("fixed-width", 300)
        column_renderer = gtk.CellRendererText()
        column.pack_start(column_renderer)
        column.set_attributes(column_renderer, text=FIRSTNAME_COLUMN_INDEX) 
        self.view.append_column(column)
        
        column = gtk.TreeViewColumn("name")
#        column.set_property("sizing", gtk.TREE_VIEW_COLUMN_FIXED)
#        column.set_property("fixed-width", 300)
        column_renderer = gtk.CellRendererText()
        column.pack_start(column_renderer)
        column.set_attributes(column_renderer, text=NAME_COLUMN_INDEX) 
        self.view.append_column(column)
        
        column = gtk.TreeViewColumn("nick")
#        column.set_property("sizing", gtk.TREE_VIEW_COLUMN_FIXED)
#        column.set_property("fixed-width", 300)
        column_renderer = gtk.CellRendererText()
        column.pack_start(column_renderer)
        column.set_attributes(column_renderer, text=NICKNAME_COLUMN_INDEX) 
        self.view.append_column(column)
        
        column = gtk.TreeViewColumn("birth-death")
#        column.set_property("sizing", gtk.TREE_VIEW_COLUMN_FIXED)
#        column.set_property("fixed-width", 300)
        column_renderer = gtk.CellRendererText()
        column.pack_start(column_renderer)
        column.set_attributes(column_renderer, text=YEAR_BIRTH_DEATH_COLUMN_INDEX) 
        self.view.append_column(column)

        column = gtk.TreeViewColumn("occupation")
#        column.set_property("sizing", gtk.TREE_VIEW_COLUMN_FIXED)
#        column.set_property("fixed-width", 300)
        column_renderer = gtk.CellRendererText()
        column.pack_start(column_renderer)
        column.set_attributes(column_renderer, text=OOCUPATION_COLUMN_INDEX) 
        self.view.append_column(column)
                

        self.view.connect("row-activated", self.on_row_activated, INDIVIDUAL_OBJECT_COLUMN_INDEX)
        

        
        
        centerview.add(self.view)
        

    def on_row_activated(self,  treeview, path, view_column,  user_data):
        call_handled_method(self._on_row_activated,treeview, path, user_data)

    def _add_indivdual_in_tree(self, parent, indi, level=1):
        sex_picture = get_gender_pixbuf(indi)
        year_birth_death = get_life_date_str(indi)
        parent_iter = self.model.append(parent, [str(level), sex_picture, indi.firstname, indi.name.upper(), indi.nickname, year_birth_death, indi.occupation, indi])
        # reccursivly add children
        for family in self.zcore.get_families_for(indi):
            for child in family.children:
                self._add_indivdual_in_tree(parent_iter, child, level+1)
        return parent_iter

        

class FamilyListView(MaegenStackableWindow):
    '''
    This pane show family list. This is a read view.
    '''
    
    def __init__(self, zcore, database_filename):
        
        self.zcore = zcore
        self.database_filename = database_filename
        MaegenStackableWindow.__init__(self, "Family list")
        
         # add app menu
        
        menu = hildon.AppMenu()
        
        aboutMenuBtn = hildon.GtkButton(gtk.HILDON_SIZE_AUTO);
        aboutMenuBtn.set_label("About");
        aboutMenuBtn.connect("clicked", show_about_dialog, None)
        menu.append(aboutMenuBtn)
        
        menu.show_all()
        self.set_app_menu(menu)

    def _on_row_activated(self, treeview, path, user_data):
        store = treeview.get_model()
        iter = store.get_iter(path)
        family,  = store.get(iter, user_data)
        # check if the activation come from a nice icon
        window = FamilyView(self.zcore, family, self.database_filename, False)
        self.program.add_window(window)
        window.show_all()


    def init_center_view(self, centerview):
        HUSB_SEX_PICTURE_COLUMN_INDEX = 0
        HUSB_FULL_NAME_COLUMN_INDEX = 1            
        HUSB_YEAR_BIRTH_DEATH_COLUMN_INDEX = 2
        WIFE_SEX_PICTURE_COLUMN_INDEX = 3        
        WIFE_FULL_NAME_COLUMN_INDEX = 4            
        WIFE_YEAR_BIRTH_DEATH_COLUMN_INDEX = 5        
        FAMILY_OBJECT_COLUMN_INDEX = 6
        self.model = gtk.ListStore(gtk.gdk.Pixbuf, str, str,gtk.gdk.Pixbuf, str, str, object)
        for family in self.zcore.retrieve_all_families():
            husb_picture = None
            husb_full_name = None
            husb_year_birth_death = ""
            
            wife_picture = None
            wife_full_name = None
            wife_year_birth_death = ""            
            
            if family.husband:
                husb_picture = get_gender_pixbuf(family.husband)                            
                indi = family.husband                           
                husb_full_name = str(indi)
                husb_year_birth_death = get_life_date_str(indi)
               
            if family.wife :
                wife_picture = get_gender_pixbuf(family.wife)
                indi = family.wife        
                wife_full_name = str(indi)                   
                wife_year_birth_death = get_life_date_str(indi)
                 
                  
            self.model.append([husb_picture, husb_full_name, husb_year_birth_death, wife_picture, wife_full_name, wife_year_birth_death, family])   
        
        self.view = gtk.TreeView(self.model)     
        self.view.set_headers_visible(True)           
        self.view.set_headers_clickable(True)
        
        column = gtk.TreeViewColumn("S")
        column_renderer = gtk.CellRendererPixbuf()
        column.pack_start(column_renderer)
        column.set_attributes(column_renderer, pixbuf=HUSB_SEX_PICTURE_COLUMN_INDEX) 
        self.view.append_column(column)
        
        column = gtk.TreeViewColumn("husband")
#        column.set_property("sizing", gtk.TREE_VIEW_COLUMN_FIXED)
#        column.set_property("fixed-width", 300)
        column_renderer = gtk.CellRendererText()
        column.pack_start(column_renderer)
        column.set_attributes(column_renderer, text=HUSB_FULL_NAME_COLUMN_INDEX) 
        self.view.append_column(column)
            
        
        column = gtk.TreeViewColumn("birth-death")
#        column.set_property("sizing", gtk.TREE_VIEW_COLUMN_FIXED)
#        column.set_property("fixed-width", 300)
        column_renderer = gtk.CellRendererText()
        column.pack_start(column_renderer)
        column.set_attributes(column_renderer, text=HUSB_YEAR_BIRTH_DEATH_COLUMN_INDEX) 
        self.view.append_column(column)



        column = gtk.TreeViewColumn("S")
        column_renderer = gtk.CellRendererPixbuf()
        column.pack_start(column_renderer)
        column.set_attributes(column_renderer, pixbuf=WIFE_SEX_PICTURE_COLUMN_INDEX) 
        self.view.append_column(column)
        
        column = gtk.TreeViewColumn("wife")
#        column.set_property("sizing", gtk.TREE_VIEW_COLUMN_FIXED)
#        column.set_property("fixed-width", 300)
        column_renderer = gtk.CellRendererText()
        column.pack_start(column_renderer)
        column.set_attributes(column_renderer, text=WIFE_FULL_NAME_COLUMN_INDEX) 
        self.view.append_column(column)
            
        
        column = gtk.TreeViewColumn("birth-death")
#        column.set_property("sizing", gtk.TREE_VIEW_COLUMN_FIXED)
#        column.set_property("fixed-width", 300)
        column_renderer = gtk.CellRendererText()
        column.pack_start(column_renderer)
        column.set_attributes(column_renderer, text=WIFE_YEAR_BIRTH_DEATH_COLUMN_INDEX) 
        self.view.append_column(column)

                

        self.view.connect("row-activated", self.on_row_activated, FAMILY_OBJECT_COLUMN_INDEX)
        

        
        
        centerview.add(self.view)
        

    def on_row_activated(self,  treeview, path, view_column,  user_data):
        call_handled_method(self._on_row_activated,treeview, path, user_data)



class NameListView(MaegenStackableWindow):
    '''
    This pane show name list. This is a read view.
    '''
    
    def __init__(self, zcore, database_filename):
        
        self.zcore = zcore
        self.database_filename = database_filename
        MaegenStackableWindow.__init__(self, "Name list")
        
         # add app menu
        
        menu = hildon.AppMenu()
        
        aboutMenuBtn = hildon.GtkButton(gtk.HILDON_SIZE_AUTO);
        aboutMenuBtn.set_label("About");
        aboutMenuBtn.connect("clicked", show_about_dialog, None)
        menu.append(aboutMenuBtn)
        
        menu.show_all()
        self.set_app_menu(menu)

    def _on_row_activated(self, treeview, path, user_data):
        store = treeview.get_model()
        iter = store.get_iter(path)
        indi,  = store.get(iter, user_data)
        if indi:
            window = IndividualView(self.zcore, indi, self.database_filename, False)
            self.program.add_window(window)
            window.show_all()


    def init_center_view(self, centerview):
        NAME_COLUMN_INDEX = 0
        COUNT_COLUMN_INDEX = 1            
        PERIOD_COLUMN_INDEX = 2
        INDIVIDUAL_COLUMN_INDEX = 3
        self.model = gtk.TreeStore(str, str, str, object)
        for name in self.zcore.retrieve_all_names():
            upper_name = name.upper()
            indi_list = self.zcore.retrieve_individual_for_name(upper_name)
            period = ""
            date_min = None
            date_max = None
                    
            for indi in indi_list:
                def calculate_life_period(date_min, date_max, life_date):
                    if life_date:
                        if date_min:
                            if life_date < date_min:
                                date_min = life_date
                        else:                        
                                date_min = life_date
                        if date_max:
                            if life_date > date_max:
                                date_max = life_date
                        else:
                                date_max = life_date
                    return (date_min,date_max)
                date_min, date_max = calculate_life_period(date_min, date_max, indi.birthDate)                       
                date_min, date_max = calculate_life_period(date_min, date_max, indi.deathDate)
                
            if date_min:
                period += str(date_min.year)
            if date_max:
                period += "-" + str(date_max.year)
                  
            root = self.model.append(None, [upper_name, len(indi_list), period, None])
            for indi in indi_list:
                life_period = get_life_date_str(indi)
                self.model.append(root, [str(indi),None, life_period, indi] )   
        
        self.view = gtk.TreeView(self.model)             
        self.view.set_headers_visible(True)           
        self.view.set_headers_clickable(True)        
        
        column = gtk.TreeViewColumn("Name")
        column_renderer = gtk.CellRendererText()
        column.pack_start(column_renderer)
        column.set_attributes(column_renderer, text=NAME_COLUMN_INDEX) 
        self.view.append_column(column)

        column = gtk.TreeViewColumn("Count")
        column_renderer = gtk.CellRendererText()
        column.pack_start(column_renderer)
        column.set_attributes(column_renderer, text=COUNT_COLUMN_INDEX) 
        self.view.append_column(column)
            
        
        column = gtk.TreeViewColumn("Period")
        column_renderer = gtk.CellRendererText()
        column.pack_start(column_renderer)
        column.set_attributes(column_renderer, text=PERIOD_COLUMN_INDEX) 
        self.view.append_column(column)




        self.view.connect("row-activated", self.on_row_activated, INDIVIDUAL_COLUMN_INDEX)
        

        
        
        centerview.add(self.view)
        

    def on_row_activated(self,  treeview, path, view_column,  user_data):   
        call_handled_method(self._on_row_activated,treeview, path, user_data)

      
      
class DefaultView(MaegenStackableWindow):
    '''
    This pane show somme statistical informations about the database
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

    def _on_add_family_clicked_event(self, widget, data):
        dialog = gtk.Dialog()
        dialog.set_transient_for(self)
        dialog.set_title("New Family")
        dialog.add_button("Create", gtk.RESPONSE_OK)
        selector = hildon.TouchSelector()
        husband_model = gtk.ListStore(str, object)
        wife_model = gtk.ListStore(str, object)
        logging.debug("creating list for husband selection...")
        for indi in self.zcore.retrieve_all_individuals():
            if indi.gender in ["male", None]:
                husband_model.append([str(indi), indi])
            elif indi.gender in ["female", None]:
                wife_model.append([str(indi), indi])
            else:
                logging.warning("unexpected gender for " + str(parent))
                husband_model.append([str(indi), indi])
                wife_model.append([str(indi), indi])
        selector.append_column(husband_model, gtk.CellRendererText(), text=0)
        selector.append_column(wife_model, gtk.CellRendererText(), text=0)
        selector.set_column_selection_mode(hildon.TOUCH_SELECTOR_SELECTION_MODE_SINGLE)
        dialog.vbox.pack_start(hildon.Caption(None, "Spouses", selector), expand=True)
        dialog.show_all()
        resu = dialog.run()
        if resu == gtk.RESPONSE_OK:
            model, iter = selector.get_selected(0)
            husband = model.get(iter, 1)[0]
            model, iter = selector.get_selected(1)
            wife = model.get(iter, 1)[0]
            dialog.destroy()
            self.zcore.create_new_family(husband, wife)
            self.zcore.save_database(self.database_filename)
            self.refresh()
        else:
            dialog.destroy()


    def _on_individual_clicked_event(self, widget, data):
        dialog = gtk.Dialog()
        dialog.set_transient_for(self)
        dialog.set_title("New individual")
        dialog.add_button("Create", gtk.RESPONSE_OK)
        firstname = hildon.Entry(gtk.HILDON_SIZE_AUTO)
        name = hildon.Entry(gtk.HILDON_SIZE_AUTO)
        nickname = hildon.Entry(gtk.HILDON_SIZE_AUTO)
        dialog.vbox.add(hildon.Caption(None, "Firstname", firstname))
        dialog.vbox.add(hildon.Caption(None, "Name", name))
        dialog.vbox.add(hildon.Caption(None, "Nickname", nickname))
        dialog.show_all()
        resu = dialog.run()
        if resu == gtk.RESPONSE_OK:
            new_indi = self.zcore.create_new_individual(name.get_text(), firstname.get_text())
            self.zcore.save_database(self.database_filename)
            self.refresh()
            new_indi.nickname = nickname.get_text()
            dialog.destroy()
            window = IndividualView(self.zcore, new_indi, self.database_filename, edit_mode=self.zcore.settings.edit_new_individual)
            self.program.add_window(window)
            window.show_all()
        else:
            dialog.destroy()


    def _on_btn_name_clicked_event(self, widget, data):
        window = NameListView(self.zcore, self.database_filename)
        self.program.add_window(window)
        window.show_all()


    def _on_btn_branch_clicked_event(self, widget, data):
        window = BranchListView(self.zcore, self.database_filename)
        self.program.add_window(window)
        window.show_all()


    def _on_btn_family_clicked_event(self, widget, data):
        window = FamilyListView(self.zcore, self.database_filename)
        self.program.add_window(window)
        window.show_all()


    def _on_btn_individual_clicked_event(self, widget, data):
        window = IndividualListView(self.zcore, self.database_filename)
        self.program.add_window(window)
        window.show_all()


    def _on_search_menu_clicked(self, widget, data):
        dialog = gtk.Dialog()
        dialog.set_transient_for(self)
        dialog.set_title("Search")
        dialog.add_button("Search", gtk.RESPONSE_OK)
        entry = hildon.Entry(gtk.HILDON_SIZE_AUTO)
        dialog.vbox.add(entry)
        dialog.show_all()
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            dialog.destroy()
            not_yet_implemented()
        else:
            dialog.destroy()


    def _on_export_menu_clicked(self, widget, data):
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
        pannable_area.set_property('mov_mode', hildon.MOVEMENT_MODE_BOTH)
        pannable_area.set_property('size-request-policy', hildon.SIZE_REQUEST_CHILDREN)
        pannable_area.add_with_viewport(gedcom)
        dialog.vbox.add(pannable_area)
        dialog.show_all()
        response = dialog.run()
        if response == -1000:
            dialog.destroy()
            fc = gobject.new(hildon.FileChooserDialog, title="Enter gedcom file", action=gtk.FILE_CHOOSER_ACTION_SAVE)
            fc.set_property('show-files', True)
            fc.set_do_overwrite_confirmation(True)
            if fc.run() == gtk.RESPONSE_OK:
                filepath = fc.get_filename()
                self.zcore.export_to_gedcom(filepath + ".ged")
            
            fc.destroy()
        
        dialog.destroy()




    def refresh(self):
        self.individual_count_label.set_value(str(self.zcore.individuals_count()))
        self.family_count_label.set_value(str(self.zcore.families_count()))
        self.branche_count_label.set_value(str(self.zcore.branches_count()))
        self.name_count_label.set_value(str(self.zcore.names_count()))


    def on_export_menu_clicked(self, widget, data):
        call_handled_method(self._on_export_menu_clicked, widget, data)

        
    def on_search_menu_clicked(self, widget, data):
        call_handled_method(self._on_search_menu_clicked,widget, data)        


    def on_btn_individual_clicked_event(self, widget, data):
         call_handled_method(self._on_btn_individual_clicked_event,widget, data)
         
    def on_btn_family_clicked_event(self, widget, data):
         call_handled_method(self._on_btn_family_clicked_event, widget, data)

    def on_btn_branch_clicked_event(self, widget, data):
        call_handled_method(self._on_btn_branch_clicked_event, widget, data)

    def on_btn_name_clicked_event(self, widget, data):
         call_handled_method(self._on_btn_name_clicked_event, widget, data)

    def init_center_view(self, centerview):
       button = hildon.Button(gtk.HILDON_SIZE_AUTO_WIDTH | gtk.HILDON_SIZE_FINGER_HEIGHT, hildon.BUTTON_ARRANGEMENT_HORIZONTAL)
       button.set_title("Individual")
       button.set_value(str(self.zcore.individuals_count()))
       button.connect("clicked", self.on_btn_individual_clicked_event, None)
       centerview.pack_start(button, expand=False)
       
       self.individual_count_label = button

       button = hildon.Button(gtk.HILDON_SIZE_AUTO_WIDTH | gtk.HILDON_SIZE_FINGER_HEIGHT, hildon.BUTTON_ARRANGEMENT_HORIZONTAL)
       button.set_title("Family")
       button.set_value(str(self.zcore.families_count()))
       button.connect("clicked", self.on_btn_family_clicked_event, None)
       centerview.pack_start(button, expand=False)
       
       self.family_count_label= button
        
       button = hildon.Button(gtk.HILDON_SIZE_AUTO_WIDTH | gtk.HILDON_SIZE_FINGER_HEIGHT, hildon.BUTTON_ARRANGEMENT_HORIZONTAL)
       button.set_title("Branch")
       button.set_value(str(self.zcore.branches_count()))        
       button.connect("clicked", self.on_btn_branch_clicked_event, None)       
       centerview.pack_start(button, expand=False)

       self.branche_count_label = button

       button = hildon.Button(gtk.HILDON_SIZE_AUTO_WIDTH | gtk.HILDON_SIZE_FINGER_HEIGHT, hildon.BUTTON_ARRANGEMENT_HORIZONTAL)
       button.set_title("Name")
       button.set_value(str(self.zcore.names_count()))            
       button.connect("clicked", self.on_btn_name_clicked_event, None)       
       centerview.pack_start(button, expand=False)

       self.name_count_label = button
    
    def init_bottom_button(self, bottomButtons):
        add_indi_btn = self.create_button("Add Individual")
        add_indi_btn.connect("clicked", self.on_add_individual_clicked_event, None)
        self.add_button(add_indi_btn)
        
        add_fami_btn = self.create_button("Add Family")
        add_fami_btn.connect("clicked", self.on_add_family_clicked_event, None)
        self.add_button(add_fami_btn)
        
    def on_add_individual_clicked_event(self, widget, data):
        call_handled_method(self._on_individual_clicked_event,widget, data)
        
    
    def on_add_family_clicked_event(self, widget, data):
        call_handled_method(self._on_add_family_clicked_event,widget, data)


class FamilyView(MaegenStackableWindow):
    '''
    This pane show details of a given family
    '''
    
    def __init__(self, zcore, family, database_filename, edit_mode=False):
        self.zcore = zcore
        self.database_filename = database_filename
        self.family = family
        self.edit_mode = edit_mode
        self.edit_husband = None
        self.edit_wife = None
        MaegenStackableWindow.__init__(self, "Family details")

                # add app menu
        
        menu = hildon.AppMenu()
                                                                                                                                                          
        if  self.edit_mode:
            add_child_btn = hildon.GtkButton(gtk.HILDON_SIZE_AUTO);
            add_child_btn.set_label("Add child");
            add_child_btn.connect("clicked", self.on_add_child_menu_clicked, None)
            menu.append(add_child_btn)    

            rem_child_btn = hildon.GtkButton(gtk.HILDON_SIZE_AUTO);
            rem_child_btn.set_label("Remove Child");
            rem_child_btn.connect("clicked", self.on_remove_child_menu_clicked, None)
            menu.append(rem_child_btn)    
            
        else:
            editBtn = hildon.GtkButton(gtk.HILDON_SIZE_AUTO);
            editBtn.set_label("Edit");
            editBtn.connect("clicked", self.on_edit_menu_clicked, None)
            menu.append(editBtn)    
        

        
        aboutMenuBtn = hildon.GtkButton(gtk.HILDON_SIZE_AUTO);
        aboutMenuBtn.set_label("About");
        aboutMenuBtn.connect("clicked", show_about_dialog, None)
        menu.append(aboutMenuBtn)
        
        
        
        menu.show_all()
        self.set_app_menu(menu)  

    def _on_child_row_activated(self, treeview, path, user_data):
        if not self.edit_mode:
            store = treeview.get_model()
            iter = store.get_iter(path)
            indi,  = store.get(iter, user_data)
            # check if the activation come from a nice icon
            hildon.WindowStack.get_default().pop_1()
            window = IndividualView(self.zcore, indi, self.database_filename, False)
            self.program.add_window(window)
            window.show_all()


    def _on_parent_clicked_event(self, widget, data):
        if self.edit_mode:
            # open a dialog an individual or create a new one
            if data == self.edit_husband:
                self._open_dialog_to_select_parent(widget, "husband")
            elif data == self.edit_wife:
                self._open_dialog_to_select_parent(widget, "wife")
            elif data == self.family.husband and self.edit_husband is None:
                self._open_dialog_to_select_parent(widget, "husband")
            elif data == self.family.wife and self.edit_wife is None:
                self._open_dialog_to_select_parent(widget, "wife")
            else:
                logging.error("unexpected data attribute " + str(data))
        else:
            hildon.WindowStack.get_default().pop_1()
            indi = data
            window = IndividualView(self.zcore, indi, self.database_filename, False)
            self.program.add_window(window)
            window.show_all()


    def _on_edit_menu_clicked(self):
        
        # remove  the currentview
        hildon.WindowStack.get_default().pop_1()
        # open the clicked parent
        window = FamilyView(self.zcore, self.family, self.database_filename, True)
        self.program.add_window(window)
        window.show_all()


    def _on_remove_child_menu_clicked(self):
        store, iter = self.view.get_selection().get_selected()
        indi,  = store.get(iter, 5)
        if iter:
            self.model.remove(iter)
            show_banner_information(str(indi) + " has been removed")
        else:
            show_banner_information("select a child to remove first")


    def _on_add_child_menu_clicked(self):
        selector = hildon.TouchSelector()
        model = gtk.ListStore(str, object)
        logging.debug("creating list for child selection...")
        for indi in filter(lambda child: child.mother is None and child.father is None, self.zcore.retrieve_all_individuals()):
            model.append([str(indi), indi])
        
        selector.append_column(model, gtk.CellRendererText(), text=0)
        selector.set_column_selection_mode(hildon.TOUCH_SELECTOR_SELECTION_MODE_SINGLE)
        dialog = hildon.PickerDialog(self)
        dialog.set_transient_for(self)
        dialog.set_title("Select an individual")
        dialog.set_done_label("add as child")
        dialog.set_selector(selector)
        dialog.show_all()
        self.selected_individual = None
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            model, iter = selector.get_selected(0)
            indi = model.get(iter, 1)[0]
            dialog.destroy()
            self.model.append(self._create_row_for_children_list_model(indi))
        else:
            dialog.destroy()


    def _on_save_clicked_event(self, widget, data):
        
        # change identity of the family
        
        # change the marriage status
        model, iter = self.edit_marriage.get_selector().get_selected(0)
        marriage = model.get(iter, 0)[0]
        if marriage == "no mention":
            param_marriage = False
        elif marriage == "married":
            param_marriage = True
        else:
            logging.error("unexpexted marriage value from picker [" + str(marriage) + "], value not set")
            param_marriage = self.family.married
        model, iter = self.edit_divorce.get_selector().get_selected(0)
        divorce = model.get(iter, 0)[0]
        if divorce == "not divorced":
            param_divorce = False
        elif divorce == "divorced":
            param_divorce = True
        else:
            logging.error("unexpexted divorce value from picker [" + str(divorce) + "], value not set")
            param_divorce = self.family.divorced
        if self.marriagedate_enable.get_active():
            y, m, d = self.edit_marriage_date.get_date()
            param_marriage_date = datetime.date(y, m + 1, d)
        else:
            param_marriage_date = None
        param_marriage_place = self.edit_marriage_place.get_text()
        if self.divorcedate_enable.get_active():
            y, m, d = self.edit_divorce_date.get_date()
            param_divorce_date = datetime.date(y, m + 1, d)
        else:
            param_divorce_date = None
        self.zcore.update_marriage_status(self.family, married=param_marriage, marriage_date=param_marriage_date, marriage_place=param_marriage_place, divorced=param_divorce, divorce_date=param_divorce_date)
        # change children list
        iter = self.model.get_iter_first()
        children_list = []
        while iter:
            indi,  = self.model.get(iter, 5)
            children_list.append(indi)
            iter = self.model.iter_next(iter)
        self.zcore.update_children_list(self.family, children_list)
        # after all job done, save the database
        self.zcore.save_database(self.database_filename)
        self.pop_and_show_family()


    def _create_row_for_children_list_model(self, indi):
        '''
        Return a sequence for given indiividual suitable for model of children list.
        parameter:
            - indi : the child as individual
        '''
        
        sex_picture = get_gender_pixbuf(indi)
        year_birth_death = get_life_date_str(indi)
        row = [sex_picture, indi.firstname, indi.name.upper(), indi.nickname, year_birth_death, indi]
        return row



    def on_save_clicked_event(self, widget, data):
        call_handled_method(self._on_save_clicked_event,widget, data)        
        
    def on_cancel_clicked_event(self, widget, data):
        call_handled_method(self.pop_and_show_family)


    def init_bottom_button(self, bottomButtons):
        logging.debug("init_bottom_button for FamilyView...")
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


    def pop_and_show_family(self):
        hildon.WindowStack.get_default().pop_1()
        # open the clicked parent
        window = FamilyView(self.zcore, self.family,self.database_filename, False)
        self.program.add_window(window)
        window.show_all()


    def on_add_child_menu_clicked(self, widget, data):
        call_handled_method(self._on_add_child_menu_clicked)
        
        
    def on_remove_child_menu_clicked(self, widget, data):        
        call_handled_method(self._on_remove_child_menu_clicked)
       
       

    def on_edit_menu_clicked(self, widget, data):
        call_handled_method(self._on_edit_menu_clicked)


    def on_parent_clicked_event(self, widget, data):
        call_handled_method(self._on_parent_clicked_event,widget, data)
        
    def _create_parent_widget(self, individual):
        widget = gtk.HBox()
        button = hildon.Button(gtk.HILDON_SIZE_AUTO_WIDTH | gtk.HILDON_SIZE_FINGER_HEIGHT, hildon.BUTTON_ARRANGEMENT_VERTICAL)
        # Set labels value
        datestr = get_life_date_str(individual)
        
        button.set_text(str(individual), datestr)
        # Set image
        image = get_gender_image(individual)
          
            
        if image : 
            button.set_image(image)
            button.set_image_position(gtk.POS_RIGHT)
                                        
        button.connect("clicked", self.on_parent_clicked_event, individual)
        widget.pack_start(button)
        if self.edit_mode:        
            if individual == self.family.husband and not self.edit_husband:
                self.edit_husband = None
            elif  individual == self.family.wife and not self.edit_wife:
                self.edit_wife = None
            elif individual == self.edit_husband:
                pass
            elif individual == self.edit_wife:
                pass
            else:
                logging.error("unexpected individual parameter " + str(individual))        
                   
            if individual == self.family.husband or individual == self.edit_husband:                
                self.husband_enabled = hildon.CheckButton(gtk.HILDON_SIZE_AUTO)
                self.husband_enabled.set_label("enabled")
                self.husband_enabled.set_active(True)
                widget.pack_start(self.husband_enabled, expand=False)
            if individual == self.family.wife or individual == self.edit_wife:                
                self.wife_enabled = hildon.CheckButton(gtk.HILDON_SIZE_AUTO)
                self.wife_enabled.set_label("enabled")
                self.wife_enabled.set_active(True)
                widget.pack_start(self.wife_enabled, expand=False)
               
        return widget

    def _open_dialog_to_select_parent(self, widget, parent):
        selector = hildon.TouchSelector()
        model = gtk.ListStore(str, object)
        logging.debug("creating list for parent selection...")
        for indi in self.zcore.retrieve_all_individuals():
            if parent == "husband":
                if indi.gender in ["male", None] and not indi == self.family.husband:
                    model.append([str(indi), indi])
            elif parent == "wife":
                if indi.gender in ["female", None] and not indi == self.family.wife:
                    model.append([str(indi), indi])
            else:
                logging.error("unexpected spouse parameter " + str(parent))
                    
        selector.append_column(model, gtk.CellRendererText(), text=0)
        selector.set_column_selection_mode(hildon.TOUCH_SELECTOR_SELECTION_MODE_SINGLE)
        def __enable_prent_checkbox(column , user_data):
            if parent == "husband":
                self.husband_enabled.set_active(True)    
            elif parent == "wife":
                self.wife_enabled.set_active(True)
            else:
                logging.error("unexpected spouse parameter " + str(parent)) 
            
        selector.connect("changed", __enable_prent_checkbox)
        
        dialog = hildon.PickerDialog(self)
        dialog.set_transient_for(self)
        dialog.set_title("Select an individual")
        dialog.set_done_label("Set as spouse")
        dialog.set_selector(selector)
        dialog.show_all()
        self.selected_individual = None
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            model, iter = selector.get_selected(0)
            indi = model.get(iter, 1)[0]
            dialog.destroy()
            if parent == "husband":
                self.edit_husband = indi
            elif parent == "wife":
                self.edit_wife = indi
            else:
                logging.error("unexpected spouse parmaeter " + str(parent))
            for child in self.spouses_pane.get_children():
                logging.debug("removing spouse widget from spouse pane...")
                self.spouses_pane.remove(child)
            logging.debug("attemting to add new spouse widget...")
            self._create_spouses_pane()
            self.spouses_pane.show_all()
        else:
            dialog.destroy()


    def open_dialog_to_select_parent(self, widget, parent):
        call_handled_method(self._open_dialog_to_select_parent,widget, parent)

    def _create_spouses_pane(self):
        if self.edit_mode:
            if self.edit_husband:
                logging.debug("add a spouse widget for edited husband " + str(self.edit_husband))
                self.spouses_pane.pack_start(self._create_parent_widget(self.edit_husband))
            elif self.family.husband:
                logging.debug("add a spouse widget for current husband " + str(self.family.husband))
                self.spouses_pane.pack_start(self._create_parent_widget(self.family.husband))
            else:
                logging.debug("add a button to set an husband")
                add_husband_btn = hildon.Button(gtk.HILDON_SIZE_AUTO_WIDTH | gtk.HILDON_SIZE_FINGER_HEIGHT, hildon.BUTTON_ARRANGEMENT_VERTICAL)
                add_husband_btn.set_title("Add husband")               
                add_husband_btn.connect("clicked", self.open_dialog_to_select_parent, "husband")
                self.spouses_pane.pack_start(add_husband_btn)
        elif self.family.husband:
            self.spouses_pane.pack_start(self._create_parent_widget(self.family.husband))
        else:
            logging.debug("no widget for husband cause there is no husband and not in edit mode")
            
        if self.edit_mode:
            if self.edit_wife:
                logging.debug("add a spouse widget for edited wife" + str(self.edit_wife))
                self.spouses_pane.pack_start(self._create_parent_widget(self.edit_wife))
            elif self.family.wife:
                logging.debug("add a spouse widget for current wife " + str(self.family.wife))                
                self.spouses_pane.pack_start(self._create_parent_widget(self.family.wife))
            else:
                logging.debug("add a button to set a wife")
                add_wife_btn = hildon.Button(gtk.HILDON_SIZE_AUTO_WIDTH | gtk.HILDON_SIZE_FINGER_HEIGHT, hildon.BUTTON_ARRANGEMENT_VERTICAL)
                add_wife_btn.set_title("Add husband")               
                add_wife_btn.connect("clicked", self.open_dialog_to_select_parent, "husband")
                self.spouses_pane.pack_start(add_wife_btn)
        elif self.family.wife:                        
            self.spouses_pane.pack_start(self._create_parent_widget(self.family.wife))
        else:
            logging.debug("no widget for wife cause there is no wife and not in edit mode")
 

    def create_spouses_pane(self):
        '''
        Create a widget containing spouses
        '''
        self.spouses_pane = gtk.HBox()                        

        self._create_spouses_pane()
        
        return self.spouses_pane
    
    
    def _create_divorce_event_detail_pane(self):
        hbox = gtk.HBox()
        self.edit_divorce_date = hildon.hildon_date_button_new_with_year_range(gtk.HILDON_SIZE_AUTO_WIDTH | gtk.HILDON_SIZE_FINGER_HEIGHT, hildon.BUTTON_ARRANGEMENT_VERTICAL, min_year=1000, max_year=datetime.date.today().year)
        self.edit_divorce_date.set_title("Date")
        self.divorcedate_enable = hildon.CheckButton(gtk.HILDON_SIZE_AUTO)
        self.divorcedate_enable.set_label("enabled")
                   
        if self.family.divorced and self.family.divorced_date:
            self.edit_divorce_date.set_date(self.family.divorced_date.year, self.family.divorced_date.month-1, self.family.divorced_date.day)        
            self.divorcedate_enable.set_active(True)
            def __enable_divorcedate_checkbox(column , user_data):
                self.divorcedate_enable.set_active(True)
            self.edit_divorce_date.get_selector().connect("changed", __enable_divorcedate_checkbox)
                    

        hbox.pack_start(self.edit_divorce_date, expand=False)
        hbox.pack_start(self.divorcedate_enable, expand=False)
                            
        self.divorce_event_detail_pane.pack_start(hbox, expand=False) 
    
 
    
    def _create_marriage_event_detail_pane(self):
                
        hbox = gtk.HBox()
        self.edit_marriage_date = hildon.hildon_date_button_new_with_year_range(gtk.HILDON_SIZE_AUTO_WIDTH | gtk.HILDON_SIZE_FINGER_HEIGHT, hildon.BUTTON_ARRANGEMENT_VERTICAL, min_year=1000, max_year=datetime.date.today().year)
        self.edit_marriage_date.set_title("Date")
        self.marriagedate_enable = hildon.CheckButton(gtk.HILDON_SIZE_AUTO)
        self.marriagedate_enable.set_label("enabled")
        
        if self.family.married and self.family.married_date:
            self.edit_marriage_date.set_date(self.family.married_date.year, self.family.married_date.month-1, self.family.married_date.day)
            self.marriagedate_enable.set_active(True)
            def __enable_marriagedate_checkbox(column , user_data):
                self.marriagedate_enable.set_active(True)
            self.edit_marriage_date.get_selector().connect("changed", __enable_marriagedate_checkbox)    

        hbox.pack_start(self.edit_marriage_date, expand=False)
        hbox.pack_start(self.marriagedate_enable, expand=False)
        
        self.marriage_event_detail_pane.pack_start(hbox, expand=False)            

                    
        self.edit_marriage_place = hildon.Entry(gtk.HILDON_SIZE_AUTO)
        if self.family.married_place:
            self.edit_marriage_place.set_text(self.family.married_place)
        else:
            self.edit_marriage_place.set_placeholder("Enter location")
        self.marriage_event_detail_pane.pack_start(hildon.Caption(None,"Place", self.edit_marriage_place), expand=False)

    
    def create_spouses_status_pane(self):
        '''
        Ceate a widget containing spouses status e.g. marriage and divorce information.
        '''
        status = gtk.VBox()
        
        if self.edit_mode:
            marriage_pane = gtk.HBox()
            
            self.edit_marriage = hildon.PickerButton(gtk.HILDON_SIZE_AUTO, hildon.BUTTON_ARRANGEMENT_VERTICAL)
            self.edit_marriage.set_title("Marriage")
            selector = hildon.TouchSelector(text=True)
            self.edit_marriage.set_selector(selector)
            selector.append_text("no mention")
            selector.append_text("married")                   
            if self.family.married:               
                self.edit_marriage.set_active(1)
            else:
                self.edit_marriage.set_active(0)
                
            def __enable_marriage_detail_widget(column , user_data):
                model, iter = self.edit_marriage.get_selector().get_selected(0)
                marriage_status = model.get(iter,0)[0]
                if marriage_status == "no mention":
                    for child in self.marriage_event_detail_pane.get_children():
                        self.marriage_event_detail_pane.remove(child)                    
                elif marriage_status == "married":
                    self._create_marriage_event_detail_pane()
                self.marriage_event_detail_pane.show_all()
                    
            self.edit_marriage.get_selector().connect("changed", __enable_marriage_detail_widget)
            marriage_pane.pack_start(self.edit_marriage, expand=False)
        
            self.marriage_event_detail_pane = gtk.HBox()
            if self.family.married : self._create_marriage_event_detail_pane()
            marriage_pane.pack_start(self.marriage_event_detail_pane, expand=False)
            
            status.pack_start(marriage_pane)
            
            divorced_pane = gtk.HBox()
            
            self.edit_divorce = hildon.PickerButton(gtk.HILDON_SIZE_AUTO, hildon.BUTTON_ARRANGEMENT_VERTICAL)
            self.edit_divorce.set_title("Divorce")
            selector = hildon.TouchSelector(text=True)
            self.edit_divorce.set_selector(selector)
            selector.append_text("not divorced")
            selector.append_text("divorced")                   
            if self.family.divorced:               
                self.edit_divorce.set_active(1)
            else:
                self.edit_divorce.set_active(0)
                
            def __enable_divorce_detail_widget(column , user_data):
                model, iter = self.edit_divorce.get_selector().get_selected(0)
                divorce_status = model.get(iter,0)[0]
                if divorce_status == "not divorced":
                    for child in self.divorce_event_detail_pane.get_children():
                        self.divorce_event_detail_pane.remove(child)                    
                elif divorce_status == "divorced":
                    self._create_divorce_event_detail_pane()
                self.divorce_event_detail_pane.show_all()
                    
            self.edit_divorce.get_selector().connect("changed", __enable_divorce_detail_widget)                
            divorced_pane.pack_start(self.edit_divorce, expand=False)


            self.divorce_event_detail_pane = gtk.HBox()
            if self.family.divorced : self._create_divorce_event_detail_pane()
            divorced_pane.pack_start(self.divorce_event_detail_pane, expand=False)
        
            
            status.pack_start(divorced_pane)
        else:
            marriage_state = "no mention"
            if self.family.married:
                marriage_state = "married"
                if self.family.married_date:
                    marriage_state += " on " + str(self.family.married_date)
                if self.family.married_place:
                    marriage_state += " at " + self.family.married_place
                        
            status.pack_start(self.justifyLeft(gtk.Label("Marriage : " + marriage_state)))
            divorced_state = "not divorced"
            if self.family.divorced:
                divorced_state = "Divorced"
                if self.family.divorced_date:
                    divorced_state += " on " + str(self.family.divorced_date)
            status.pack_start(self.justifyLeft(gtk.Label(divorced_state)))
        
        return status
    


    
    
    def on_child_row_activated(self,  treeview, path, view_column,  user_data):
        call_handled_method(self._on_child_row_activated,treeview, path, user_data)
    
    def create_children_pane(self):
 
        
        SEX_PICTURE_COLUMN_INDEX = 0
        FIRSTNAME_COLUMN_INDEX = 1
        NAME_COLUMN_INDEX = 2
        NICKNAME_COLUMN_INDEX = 3
        YEAR_BIRTH_DEATH_COLUMN_INDEX = 4
        INDIVIDUAL_OBJECT_COLUMN_INDEX = 5
        self.model = gtk.ListStore(gtk.gdk.Pixbuf, str, str, str, str, object)
        for indi in self.family.children:
            
            row = self._create_row_for_children_list_model(indi)
            self.model.append(row)   
        
        self.view = gtk.TreeView(self.model)     
        self.view.set_headers_visible(True)           
        self.view.set_headers_clickable(True)
        
        column = gtk.TreeViewColumn("S")
        column_renderer = gtk.CellRendererPixbuf()
        column.pack_start(column_renderer)
        column.set_attributes(column_renderer, pixbuf=SEX_PICTURE_COLUMN_INDEX) 
        self.view.append_column(column)
        
        column = gtk.TreeViewColumn("firstname")
        column_renderer = gtk.CellRendererText()
        column.pack_start(column_renderer)
        column.set_attributes(column_renderer, text=FIRSTNAME_COLUMN_INDEX) 
        self.view.append_column(column)
        
        column = gtk.TreeViewColumn("name")
        column_renderer = gtk.CellRendererText()
        column.pack_start(column_renderer)
        column.set_attributes(column_renderer, text=NAME_COLUMN_INDEX) 
        self.view.append_column(column)
        
        column = gtk.TreeViewColumn("nick")
        column_renderer = gtk.CellRendererText()
        column.pack_start(column_renderer)
        column.set_attributes(column_renderer, text=NICKNAME_COLUMN_INDEX) 
        self.view.append_column(column)
        
        column = gtk.TreeViewColumn("birth-death")
        column_renderer = gtk.CellRendererText()
        column.pack_start(column_renderer)
        column.set_attributes(column_renderer, text=YEAR_BIRTH_DEATH_COLUMN_INDEX) 
        self.view.append_column(column)

               

        self.view.connect("row-activated", self.on_child_row_activated, INDIVIDUAL_OBJECT_COLUMN_INDEX)

        children = gtk.VBox()
        children.add(self.justifyLeft(gtk.Label(str(len(self.family.children)) + " child(ren)")))
        children.add(self.view)                    
        return children
        
    def init_center_view(self, centerview):
        frame = gtk.Frame("Spouses")
        frame.add(self.create_spouses_pane())        
        centerview.pack_start(frame, expand=False,padding=5 )
        
        frame = gtk.Frame("Marriage")
        frame.add(self.create_spouses_status_pane())        
        centerview.pack_start(frame, expand=False,padding=5 )
        
        
        frame = gtk.Frame("Children")
        frame.add(self.create_children_pane())
        centerview.pack_start(frame,expand=False, padding=5)



class IndividualView(MaegenStackableWindow):
    '''
    This pane show somme detail of an individual
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
            editBtn.connect("clicked", self.on_edit_menu_clicked, None)
            menu.append(editBtn)   
            
            editBtn = hildon.GtkButton(gtk.HILDON_SIZE_AUTO);
            editBtn.set_label("Descendants");
            editBtn.connect("clicked", self.on_descednants_menu_clicked, None)
            menu.append(editBtn)   
            
        

        
        aboutMenuBtn = hildon.GtkButton(gtk.HILDON_SIZE_AUTO);
        aboutMenuBtn.set_label("About");
        aboutMenuBtn.connect("clicked", show_about_dialog, None)
        menu.append(aboutMenuBtn)
        
        
        
        menu.show_all()
        self.set_app_menu(menu)  

    def _on_parent_clicked_event(self, widget, data):
        if self.edit_mode:
            # open a dialog an individual or create a new one
            if data == self.edit_father:
                self._open_dialog_to_select_parent(widget, "father")
            elif data == self.edit_mother:
                self._open_dialog_to_select_parent(widget, "mother")
            elif data == self.individual.father and self.edit_father is None:
                self._open_dialog_to_select_parent(widget, "father")
            elif data == self.individual.mother and self.edit_mother is None:
                self._open_dialog_to_select_parent(widget, "mother")
            else:
                logging.error("unexpected data attribute " + str(data))
        # remove  the currentview
        else:
            hildon.WindowStack.get_default().pop_1()
            # open the clicked parent
            window = IndividualView(self.zcore, data, self.database_filename)
            self.program.add_window(window)
            window.show_all()


    def _on_partner_clicked_event(self, data):
        
        # remove  the currentview
        hildon.WindowStack.get_default().pop_1()
        # open the clicked parent
        window = IndividualView(self.zcore, data, self.database_filename)
        self.program.add_window(window)
        window.show_all()


    def _on_child_clicked_event(self, data):
        
        # remove  the currentview
        hildon.WindowStack.get_default().pop_1()
        # open the clicked parent
        window = IndividualView(self.zcore, data, self.database_filename)
        self.program.add_window(window)
        window.show_all()


    def _on_edit_menu_clicked(self, widget, data):
        
        # remove  the currentview
        hildon.WindowStack.get_default().pop_1()
        # open the clicked parent
        window = IndividualView(self.zcore, self.individual, self.database_filename, True)
        self.program.add_window(window)
        window.show_all()


    def _on_descednants_menu_clicked(self, widget, data):
        window = GenealogicalTreeView(self.zcore, self.individual)
        self.program.add_window(window)
        window.show_all()


    def on_descednants_menu_clicked(self, widget, data):
        call_handled_method(self._on_descednants_menu_clicked,widget, data)

    
    def pop_and_show_individual(self):
        hildon.WindowStack.get_default().pop_1()
        # open the clicked parent
        window = IndividualView(self.zcore, self.individual,self.database_filename, False)
        self.program.add_window(window)
        window.show_all()


    def on_edit_menu_clicked(self, widget, data):
        call_handled_method(self._on_edit_menu_clicked,widget, data)

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
 
    def _on_save_clicked_event(self, widget, data):
        if self.edit_father and self.edit_mother:
            if self.father_enabled.get_active() and self.mother_enabled.get_active():                            
                self.zcore.set_parents(self.individual, self.edit_father, self.edit_mother)
            else:
                if not self.father_enabled.get_active() and not self.mother_enabled.get_active():
                    self.zcore.remove_parents(self.individual)
                else:
                    if self.father_enabled.get_active():
                        self.zcore.set_father(self.individual, self.edit_father)
                        if self.individual.mother:
                            self.zcore.remove_mother(self.individual)
                    else:
                        self.zcore.set_mother(self.individual, self.edit_mother)
                        if self.individual.father:                                        
                            self.zcore.remove_father(self.individual)
        else:
            if self.edit_father is None and self.edit_mother is None:
                if self.individual.father and self.individual.mother:
                    if not self.father_enabled.get_active() and  not self.mother_enabled.get_active():                    
                        self.zcore.remove_parents(self.individual)
                    else:
                        if not self.father_enabled.get_active():
                            self.zcore.remove_father(self.individual)
                        elif not self.mother_enabled.get_active():
                            self.zcore.remove_mother(self.individual)                            
                else:
                    if self.individual.father: 
                        if not self.father_enabled.get_active():                    
                            self.zcore.remove_father(self.individual)
                    elif self.individual.mother:
                        if not self.mother_enabled.get_active():                        
                            self.zcore.remove_mother(self.individual)
                        
            else:
                if self.edit_father:
                    if self.father_enabled.get_active():                
                        self.zcore.set_father(self.individual,self.edit_father)
                    else:                    
                        if self.individual.father :
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
         
    def on_save_clicked_event(self, widget, data):
        call_handled_method(self._on_save_clicked_event,widget, data)                    
        
    def on_cancel_clicked_event(self, widget, data):
        call_handled_method(self.pop_and_show_individual)

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
                add_mother_btn.connect("clicked", self.open_dialog_to_select_parent, "mother")
                self.parent_pane.pack_start(add_mother_btn)
        elif individual.mother:
            self.parent_pane.pack_start(self._create_parent_widget(individual.mother))
        else:
            logging.debug("no widget for mother becaue there is no mother and not in edit mode")

    def _open_dialog_to_select_parent(self, widget, data):
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
            if parent == "father" and (self.individual.father or self.edit_father):
                self.father_enabled.set_active(True)    
            elif parent == "mother" and (self.individual.mother or self.edit_mother):
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
        
    
    def open_dialog_to_select_parent(self, widget, parent):
        call_handled_method(self._open_dialog_to_select_parent,widget, parent)

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




    def _create_parent_widget(self, individual):
        widget = gtk.HBox()
        button = hildon.Button(gtk.HILDON_SIZE_AUTO_WIDTH | gtk.HILDON_SIZE_FINGER_HEIGHT, hildon.BUTTON_ARRANGEMENT_VERTICAL)
        # Set labels value
        datestr = get_life_date_str(individual)
        
        button.set_text(str(individual), datestr)
        # Set image
        image = get_gender_image(individual)
          
        if image:    
            button.set_image(image)
            button.set_image_position(gtk.POS_RIGHT)
                                        
        button.connect("clicked", self.on_parent_clicked_event, individual)
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
        datestr = get_life_date_str(individual)
        
        button.set_text(str(individual), datestr)
        # Set image
        image = get_gender_image(individual)
          
        if image:    
            button.set_image(image)
            button.set_image_position(gtk.POS_RIGHT)
                                        
        button.connect("clicked", self.on_partner_clicked_event, individual)
        widget.pack_start(button)

               
        return widget
    
    def _create_child_widget(self, individual):
        widget = gtk.HBox()
        button = hildon.Button(gtk.HILDON_SIZE_AUTO_WIDTH | gtk.HILDON_SIZE_FINGER_HEIGHT, hildon.BUTTON_ARRANGEMENT_VERTICAL)
        # Set labels value
        datestr = get_life_date_str(individual)
        
        button.set_text(str(individual), datestr)
        # Set image
        image = get_gender_image(individual)
          
        if image:    
            button.set_image(image)
            button.set_image_position(gtk.POS_RIGHT)
                                        
        button.connect("clicked", self.on_child_clicked_event, individual)
        widget.pack_start(button)

               
        return widget
    
        
    def on_child_clicked_event(self, widget, data):
            call_handled_method(self._on_child_clicked_event,data)
    
    
    def on_partner_clicked_event(self, widget, data):
            call_handled_method(self._on_partner_clicked_event,data)
    
    
    def on_parent_clicked_event(self, widget, data):
        call_handled_method(self._on_parent_clicked_event,widget, data)
    

    def create_header(self, individual):
        header = gtk.HBox()
        
        # Identification
        identification = gtk.VBox()
    
        # gender
        if self.edit_mode :
            self.edit_gender_picker = self._create_gender_picker(individual)
            identification.pack_start(self.edit_gender_picker, expand=False)
        else:
            image = get_gender_image(individual)
            if image:
                identification.pack_start(self.justifyLeft(image))
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
            union.pack_start(self.justifyLeft(gtk.Label("with")), expand=False)
            if other:                                
                union.pack_start(self._create_partner_widget(other),expand=False)
            else:
                union.pack_start(self.justifyLeft(gtk.Label("unknown partner")), expand=False)            
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

    
class SplashScreenView(MaegenStackableWindow):
    '''
    This is the first view of the application e.g. the main view.  
    '''

    def init_center_view(self, centerview):
        fill_widget_with_logo(centerview)


class GenealogicalTreeView(MaegenStackableWindow):
    '''
    This pane display the genealogical data as a tree
    '''
    

    
    def __init__(self, zcore, individual, show_spouse=False):
        self.root = individual
        self.zcore = zcore
        self.show_spouse=show_spouse
   
        MaegenStackableWindow.__init__(self, title="Tree")

     

    def init_center_view(self, centerview):

         centerview.add(GenTree(self.zcore, self.root, self.show_spouse))

            
            
        
        
      
