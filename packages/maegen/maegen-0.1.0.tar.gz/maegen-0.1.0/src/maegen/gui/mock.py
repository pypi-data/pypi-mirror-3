'''
Created on Oct 14, 2011

@author: maemo
'''

from datetime import date

from maegen.core import  maegen


from maegen.common import version

version.getInstance().submitRevision("$Revision: 155 $")

class Maegen(maegen.Maegen):
    '''
    Mock class for Maegen
    '''
    
    def __init__(self):
        '''
        Create a dummy database for GUI testing
        '''
        maegen.Maegen.__init__(self)
        self.database = maegen.Database()
        

    
    def load_database(self, database_file):
        '''
        Return a dully database with some individuals
        '''
        self.database = maegen.Database()
        indi1 = self.create_new_individual("Dupont", "Jean")
        indi1.occupation = "Tailor"
        indi1.gender = "male"
        indi = self.create_new_individual("Moore", "Roger")
        indi.birthDate = date(1943,5,24)
        indi.gender = "male"
        indi2 = self.create_new_individual("Louise", "Alberta")
        indi2.birthDate = date(1913,9,11)
        indi2.deathDate = date(1995,8,30)
        indi2.gender = "female"
              
        self.make_child(indi,   self.create_new_family(indi1, indi2))
        
        
        
    
    
