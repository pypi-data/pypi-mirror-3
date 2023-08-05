# -*- encoding: UTF-8 -*-

#    Pyjama is a python project bootstraper for Maemo5 development
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
setup(name='pyjama',
      version='0.1.0',
      package_dir = {'': 'src'},
      packages=find_packages(where='src'),               
      scripts=['scripts/pyjama'],
      package_data={'pyjama': ['*.png','*.jpg']},      
      data_files=[('/usr/share/applications/hildon',['hildon/pyjama.desktop']),
                  ('/usr/share/icons/hicolor/48x48/hildon',['hildon/icons/48x48/pyjama.png']),
                  ('/usr/share/icons/hicolor/64x64/hildon',['hildon/icons/64x64/pyjama.png'])],    
      install_requires=["gdata>=2.0.9,<=2.0.14"],
      author='Thierry Bressure',
      author_email='thierry@bressure.net',
      maintainer='Thierry Bressure',
      maintainer_email='pyjama@bressure.net',
      url='http://blog.pyjama.bressure.net',
      download_url='http://pyjama.bressure.net',
      description='Pyjama is a python project bootstraper for Maemo5 development',
      long_description='Pyjama is a python project bootstraper for Maemo5 development. It generate the project structure ready for build and run',
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

