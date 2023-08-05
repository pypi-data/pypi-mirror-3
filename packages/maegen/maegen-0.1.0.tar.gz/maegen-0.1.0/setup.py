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
Created on 20 Oct. 2011

@author: thierry
'''
import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages
setup(name='maegen',
      version='0.1.0',
      package_dir = {'': 'src'},
      packages=find_packages(where='src'),               
      scripts=['scripts/maegen'],
      package_data={'maegen': ['*.png','*.jpg']},      
      data_files=[('/usr/share/applications/hildon',['hildon/maegen.desktop']),
                  ('/usr/share/icons/hicolor/48x48/hildon',['hildon/icons/48x48/maegen.png']),
                  ('/usr/share/icons/hicolor/64x64/hildon',['hildon/icons/64x64/maegen.png'])],    
      author='Thierry Bressure',
      author_email='thierry@bressure.net',
      maintainer='Thierry Bressure',
      maintainer_email='maegen@bressure.net',
      url='http://blog.maegen.bressure.net',
      download_url='http://maegen.bressure.net',
      description='Maegen is a genealogical application for N900',
      long_description='Maegen let you to collect genealogical information on the go and export then in GEDCOM format',
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          "Environment :: Handhelds/PDA's",          
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Developers',          
          'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python'          
          ],
          zip_safe=False
   
      )

