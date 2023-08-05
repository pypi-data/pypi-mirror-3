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
from exceptions import  *
from gedcom import *

import logging
import pickle
import os
import os.path


from ..common import version 

version.getInstance().submitRevision("$Revision: 155 $")

def get_maegen_storage_dir():
    '''
    Compute the application storage dir.
    This is an utility function to retrieve the directory where maegen can
    store any file like settings or cached data.
    '''
    storage = os.path.expanduser("~")    
    storage = os.path.join(storage, ".maegen")
    return storage

class Maegen(object):
    '''
    Main class of the Program. The GUI use this class like a Facade to any core functions.
    '''
    
    def __init__(self):
        self._ensure_maegen_conf_store()
        settings = None
        self.database = None
        self.load_settings()
        self.apply_settings()

    def get_maegen_settings_file(self):
        storage = get_maegen_storage_dir()
        storage = os.path.join(storage, "settings.pickle")
        return storage

    def load_settings(self):
        '''
        load the saved settings
        '''
        self._ensure_maegen_conf_store()
        storage = self.get_maegen_settings_file()
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
        self._ensure_maegen_conf_store()
        storage = self.get_maegen_settings_file()
        try:           
            file = open(storage,'wb')
            pickle.dump(self.settings,file)
            file.close()
        except IOError:
            logging.warning("failed to save the settings")

    
    def apply_settings(self):
        pass
       
        
        
    
    def _ensure_maegen_conf_store(self):
        storage = get_maegen_storage_dir()
        if os.path.exists(storage):
            pass
        else:
            os.makedirs(storage)

        

    
    def _save_database(self, filename):
        '''
        Save the current database into a file
        '''        
        storage = filename
        try:           
            file = open(storage,'wb')
            pickle.dump(self.database,file)
            file.close()
        except IOError:
            logging.error("failed to save the database")
            raise
    
    def _load_database(self, filename):
        '''
        Read a database from a file. The new database become the current database. 
        '''                
        storage = filename
        try:           
            file = open(storage,'rb')
            self.database = pickle.load(file)
            file.close()
        except IOError, EOFError:
            logging.error("failed to load the database")
            raise 
    
    '''
    Facade function
    '''
    
    def export_to_gedcom(self, filepath=None):
        '''
        Return the gedcom for current database
        Parameter:
          - filepath the file were the gedcom is written if supplied
        '''
        gedcom_str =  GedcomWriter(self.database).export()
        if filepath:
            f = open(filepath,'w')
            try:
                f.write(gedcom_str)
            finally:
                f.close()
        return gedcom_str
    
    def get_families_for_parents(self, father, mother):
        '''
        Return all family for given father and mother
        '''
        return filter(lambda fam: fam.husband == father and fam.wife == mother, self.database.families)
    
    def get_families_for(self, individual):
        '''
        Return all family where the given individual is a parent.
        '''
        def is_parent_in(individual):
            return lambda fam: individual  in [fam.husband, fam.wife] 
            
        return filter(is_parent_in(individual), self.database.families)
    
    def get_family_with_child(self, individual):
       '''
       Return family where given individual is child.
       Raise MaegenIntegrityException if more than one family are candidate
       '''
       result = filter(lambda x: individual in x.children, self.database.families)
       if len(result) > 1:
           # since we only trace genetic filiation at most ONE family is possible       
           raise MaegenIntegrityException("individual " + individual + " is child of more than one family")
       elif len(result) == 1:
           return result[0]
       else:
           return None
   
    
    def individuals_count(self):
        '''
        Return the number of individual in the current database
        '''
        return len(self.database.individuals)
    
    def families_count(self):
        '''
        Return the number of families in the current database
        '''
        return len(self.database.families)
    
    def branches_count(self):
        '''
        Return the count of branches (tree) in the database
        '''
        logging.warning("not yet implemented")
        return 0
    
    def names_count(self):
        '''
        return the count of patronymic name in the database
        '''
        logging.warning("not yet implemented")
        return 0

    def create_new_individual(self, name="inconnu", firstname="inconnu"):
        '''
        Create a new individual and add it to the database
        Return a new individual
        '''
        resu = Individual()
        resu.name = name
        resu.firstname = firstname
        self.database.individuals.add(resu)       
        return resu
    
    def create_new_family(self, husband, wife):
        '''
        Create a new family
        '''
        resu = Family()
        resu.husband = husband
        resu.wife = wife
        self.database.families.add(resu)
        return resu
    
    def make_child(self,individual, family):
        '''
        Promote the given individual to child of given family 
        '''
        family.children.append(individual)
        individual.father = family.husband
        individual.mother = family.wife
     
    def remove_father(self, individual):
        '''
        remove the father of an individual.
        Return the removed father.
        '''    
        old = individual.father
        self.set_father(individual, None)
        return old
    
  
    def remove_mother(self, individual):
        '''
        remove the mother of an individual.
        Return the removed mother.
        '''    
        old = individual.mother
        self.set_mother(individual, None)
        return old    

    def set_parents(self, individual, father, mother):
        '''
        Make an individual children of a given father and mother
        '''    
        old_father = individual.father
        old_mother = individual.mother
        individual.fathe = father
        individual.mother = mother
        
        if old_father or old_mother:
            # ensure correctness of database 
        
            # remove from the old family
            family = self.get_family_with_child(individual)
            if family:
                if family.husband == old_father or family.wife == old_mother:
                    family.children.remove(individual)
                
        # add in a family
        fam_list = self.get_families_for_parents(father, mother)
        if len(fam_list) == 1:
            # use this family
            fam = fam_list[0]
            self.make_child(individual, fam)
        else:
            # create a new one
            new_family = self.create_new_family(father,mother)
            self.make_child(individual, new_family)

    
    def set_father(self, individual, father):
        '''
        Give a father to an individual        
        '''
        old = individual.father
        individual.father = father
        if old:
            # ensure correctness of database 
        
            # remove from the old family
            family = self.get_family_with_child(individual)
            if family:
                if family.husband == old:
                    family.children.remove(individual)
        
        # add in new family
        family = self.get_family_with_child(individual)
        if family:
            # individual is already child of a family
            if family.husband == None:
                # promote the father as husband 
                family.husband = father
            elif not family.husband == father:
                raise MaegenIntegrityException(str(individual) + " is already child in a family with an husband, cannot change husband")
        elif father:
            #create a new family with fatrher as husband
            new_family = self.create_new_family(father, None)
            self.make_child(individual, new_family)
        elif individual.mother:
            # create a family with mother as wife
            new_family = self.create_new_family(None, individual.mother)
            self.make_child(individual, new_family)
            
            
        return old

    def set_mother(self, individual, mother):
        '''
        Give a mother to an individual        
        '''
        old = individual.mother
        individual.mother = mother
        if old:
            # ensure correctness of database 
        
            # remove from the old family
            family = self.get_family_with_child(individual)
            if family:
                if family.wife == old:
                    family.children.remove(individual)
        
        # add in new family
        family = self.get_family_with_child(individual)
        if family:
            # individual is already child of a family
            if family.wife == None:
                # promote the mother as husband 
                family.wife = mother
            elif not family.husband == mother:
                raise MaegenIntegrityException(str(individual) + " is already child in a family with a wife, cannot change wife")
        elif mother:
            #create a new family with mother as wife
            new_family = self.create_new_family(None, mother)
            self.make_child(individual, new_family)
        elif individual.father:
            # create a new family with father ashusband
            new_family = self.create_new_family(individual.father, None)
            self.make_child(individual, new_family)
        return old
        
    
    def retrieve_all_individuals(self):
        '''
        return all individuals in the database as a list
        '''
        return list(self.database.individuals)
    
    def retrieve_all_families(self):
        '''
        return all families in the database as a list
        '''
        return list(self.database.families)
        

    def get_maegen_storage_dir(self):
        '''
        Storage location of megen database
        '''
        return get_maegen_storage_dir()

    
    def load_database(self, database_file):
        '''
        Read a database from a file
        '''        
        self._load_database(database_file)


    def save_database(self, database_file):
        '''
        Write current database into a file
        '''
        self._save_database(database_file)
        
    def create_new_database(self, database_file):
        '''
        Create a new empty database
        '''
        self.database = Database()
        self._save_database(database_file)
        
class Settings():
    '''
    Represents the settings for Maegen
    '''
   
    def __init__(self):
        self.edit_new_individual = False

    
        
'''
Model of genealogical data
'''

# TODO move model into a python miodule

class Database(object):
    """
    genealogical data consist in a set of individuals related by a set of families
    """
    def __init__(self):
        self.individuals = set([])
        self.families = set([])

class Individual(object):
    '''
    A person
    '''
    def __init__(self):
        self.name = ""
        self.firstname = ""
        self.nickname = ""        
        self.gender = None
        
        self.birthDate = None
        self.birthPlace = ""        
        self.deathDate = None
        self.deathPlace = ""
        
        self.note = ""
        
        self.father = None
        self.mother = None
        
        self.occupation = ""

    def __str__(self, *args, **kwrgs):
        return self.firstname.capitalize() + " " + self.name.upper()

    
    
    
class Family(object):
    '''
    A family
    '''
    
    def __init__(self):
        self.husband = None
        self.wife = None
        self.married = False
        self.divorced = False
        self.divorced_date= None
        self.married_date = None
        self.married_place = ""
        
        self.children = []
                

            