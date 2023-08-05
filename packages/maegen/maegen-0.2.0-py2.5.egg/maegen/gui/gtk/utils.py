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

import gtk


from maegen.common import version

version.getInstance().submitRevision("$Revision: 78 $")

def get_gender_image(individual):
    '''
    Return a gtk.Image according to gender of given individual.
    '''
    image = None
    pixbuf = get_gender_pixbuf(individual)
    if pixbuf:
        image = gtk.Image()
        image.set_from_pixbuf(pixbuf)
    return image

def get_gender_pixbuf(individual):
    '''
    Return a pixbuf according to gender of given individual.
    '''
    pixbuf = None
    if individual.gender:
        if individual.gender == "male":
            pixbuf = gtk.gdk.pixbuf_new_from_file("male.png")           
        elif individual.gender == "female":
            pixbuf = gtk.gdk.pixbuf_new_from_file("female.png")
    return pixbuf

def fill_widget_with_logo(centerview):
    pixbuf = gtk.gdk.pixbuf_new_from_file("maegen-logo.jpg")
    for i in range(1,4):
        hbox = gtk.HBox()
        for j in range(1,5):                
            image = gtk.Image()
            image.set_from_pixbuf(pixbuf)
            hbox.add(image)
        centerview.add(hbox)
        
def get_life_date_str(indi):
    year_birth_death = ""
    if indi.birthDate:
        year_birth_death += str(indi.birthDate.year)
        
    if indi.deathDate:
        year_birth_death += "-" + str(indi.deathDate.year)
        
    return year_birth_death



                    