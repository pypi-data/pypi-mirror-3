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


from maegen.core import maegen

from optparse import OptionParser

import logging

from maegen.common import version 


version.getInstance().submitRevision("$Revision$")


LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL}




def showGui(mock=False):
    from maegen.gui.maegenGui import MaegenGui 
    gui = MaegenGui(mock)
    gui.run()
    

    
 

    
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
   parser.add_option("-m","--mock",action="store_true", dest="mock", default=False, help="start a mocked application with test data")
   parser.add_option("-l", "--log", action="store", type="string", dest="level_name", help="log level")
      
   (options, args) = parser.parse_args()
   
   level = LEVELS.get(options.level_name, logging.NOTSET)
   logging.basicConfig(level=level)

   
   showGui(mock=options.mock)




if __name__ == '__main__':  
    run()
