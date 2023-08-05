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
Created on Nov 2, 2011

@author: maemo
'''

from string import Template

from ..common import version 

version.getInstance().submitRevision("$Revision: 155 $")

class GedcomWriter():
    '''
    This class can export a maegen database into GEDCOM format 
    '''
    def __init__(self, database):
        '''
        Create a writer that can export a maegen database into GEDCOM format
        Parameter:
            - database : the maegen database
        '''
        self.database = database
        self.individual_count = 0
        self.family_count = 0
        self.individual_dic = {}
        self.family_dic = {}


    
    
    
    def export(self):
        '''
        Return a GEDCOM string for the current database
        '''
        self._give_id_to_individuals()
        self._give_id_to_families()
        return self._create_header() + self._create_submitter() + self._create_records() + self._create_trlr()


        

    def _give_id_to_individuals(self):
        for indi in self.database.individuals:
            self.individual_count += 1
            self.individual_dic[id(indi)] = self.individual_count
            
    def _give_id_to_families(self):
        for fam in self.database.families:
            self.family_count += 1
            self.family_dic[id(fam)] = self.family_count 
    
        
    def _create_header(self):
        '''
        Return the header for the current database
        '''
        header = \
"""0 HEAD
1 SOUR Maegen
2 VERS $version_of_maegen
1 SUBM @SUBMITTER@ 
1 GEDC
2 VERS 5.5
2 FORM LINEAGE-LINKED    
1 CHAR ASCII  
"""        
        return Template(header).substitute(version_of_maegen="1.0")
    
    def _create_submitter(self):
        submitter = \
"""0 @SUBMITTER@ SUBM
1 NAME $submitter
""" 
        # TODO replace maemo by the user name    
        return Template(submitter).substitute(submitter="maemo")



    def _create_personal_name_structure(self, indi, indent=1):
        """
        Return the GEDCOM part for the name of given individual
        """
        resu = ""
        name_personal = ""
        if indi.firstname :
            name_personal += indi.firstname
        else:
            name_personal += "?"
        if indi.name:
            name_personal += " /" + indi.name + "/"
        else:
            name_personal += " /?"
        resu += str(indent) + " NAME " + name_personal + "\n"
        if indi.nickname:
            resu += str(indent + 1) + NICK + indi.nickname + "\n"
        return resu
    
    
    def _convert_date_for_geneweb(self, date):
        month = None
        if date.month == 1:
            month = "JAN"
        elif date.month == 2:
            month = "FEB"
        elif date.month == 3:
            month = "MAR"
        elif date.month == 4:
            month = "APR"
        elif date.month == 5:
            month = "MAY"
        elif date.month == 6:
            month = "JUN"
        elif date.month == 7:
            month = "JUL"
        elif date.month == 8:
            month = "AUG"
        elif date.month == 9:
            month = "SEP"
        elif date.month == 10:
            month = "OCT"
        elif date.month == 11:
            month = "NOV"
        elif date.month == 12:
            month = "DEC"
            
        return  Template("$day $month $year").substitute(day=str(date.day), month=month, year=date.year)
    

    def _create_date_event_detail(self, date, indent):
        return str(indent) + " DATE " + self._convert_date_for_geneweb(date) + "\n"    
    
    def _create_birth_event(self, indi, indent=1):
        """
        Return the birth event for given individual
        """
        resu = ""
        resu += str(indent) + " BIRT\n"
        resu += self._create_date_event_detail(indi.birthDate, indent+1)
        
        return resu
    
    def _create_death_event(self, indi, indent=1):
        """
        Return the death event for given individual
        """
        resu = ""
        resu += str(indent) + " DEAT\n"
        resu += self._create_date_event_detail(indi.deathDate, indent+1)
        
        return resu

    def _create_occupation_event(self, indi, indent=1):
        """
        Return the occupation event for given individual
        """
        return str(indent) + " OCCU " + indi.occupation + "\n"
        
        
        return resu

    def _create_individual_event_structures(self, indi, indent=1):   
        resu = "" 
        if indi.birthDate:
            resu += self._create_birth_event(indi, indent)
        if indi.deathDate:
            resu+= self._create_death_event(indi, indent)

        return resu
    
    def _create_individual_attribute_structures(self, indi, indent=1):   
        resu = "" 
        if indi.occupation:
            resu += self._create_occupation_event(indi, indent)


        return resu    
    

    
    def _retrieve_individual_xref(self, individual):
        return "I" + str(self.individual_dic[id(individual)])
    
        
    def _retrieve_family_xref(self, family):
        return "F" + str(self.family_dic[id(family)])
        
    
    
    def _create_child_to_family_link(self, indi, indent=1):
        """
        Return GEDCOM line for family child link
        """
        resu = ""
        fam_list = filter(lambda f: indi in f.children, self.database.families)
        for fam in fam_list:
            resu += str(indent) + " FAMC @" + self._retrieve_family_xref(fam) + "@\n";
        return resu
        
    def _create_spouse_to_family_link(self, indi, indent=1):
        """
        Return GEDCOM line for family spouse link
        """
        resu =  ""
        fam_list = filter(lambda f: indi == f.husband or indi == f.wife, self.database.families)
        for fam in fam_list :
            resu += str(indent) + " FAMS @" + self._retrieve_family_xref(fam) + "@\n";
        return resu        
    
    

    def _create_individuals(self, indent=0):
        """
        Return all individuals in database in GEDCOM format
        """
        resu = ""
        for indi in self.database.individuals:
            resu += str(indent) + " @" + self._retrieve_individual_xref(indi) + "@ INDI\n"
            resu += self._create_personal_name_structure(indi, indent+1)
            if indi.gender == "male":
                resu += str(indent+1) + " SEX M\n"
            elif indi.gender == "female":
                resu += str(indent+1) + " SEX F\n"
            resu += self._create_individual_event_structures(indi, indent+1)
            resu += self._create_individual_attribute_structures(indi, indent+1)
            resu += self._create_child_to_family_link(indi, indent+1)
            resu += self._create_spouse_to_family_link(indi, indent+1)

        return resu
    
    def _create_families(self, indent=0):
        """
        Return all families in database in GEDCOM format
        """
        resu = ""
        for fam in self.database.families:
            resu += str(indent) + " @" + self._retrieve_family_xref(fam) + "@ FAM\n"
            if fam.husband:
                resu += str(indent+1)+ " HUSB @" + self._retrieve_individual_xref(fam.husband) + "@\n" 
            if fam.wife:
                resu += str(indent+1)+ " WIFE @" + self._retrieve_individual_xref(fam.wife) + "@\n"
            for child in fam.children:
                resu += str(indent+1)+ " CHIL @" + self._retrieve_individual_xref(child) + "@\n" 
 

        return resu
        
        
    def _create_records(self):
        """
        Return all record in GEDCOM format
        """
        return self._create_individuals()+ self._create_families()
    
    def _create_trlr(self):
        return "0 TRLR"
    
    
