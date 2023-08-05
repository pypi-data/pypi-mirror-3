${HEADER}

'''
Created on ${DATE_TIME}

@author: ${AUTHOR}
'''

import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages
setup(name='${NAME}',
      version='${VERSION}',
      package_dir = {'': 'src'},
      packages=find_packages(where='src'),               
      scripts=['scripts/${NAME}'],
      package_data={'${NAME}': ['*.png','*.jpg']},      
      data_files=[('/usr/share/applications/hildon',['hildon/${NAME}.desktop']),
                  ('/usr/share/icons/hicolor/48x48/hildon',['hildon/icons/48x48/${NAME}.png']),
                  ('/usr/share/icons/hicolor/64x64/hildon',['hildon/icons/64x64/${NAME}.png'])],    
      install_requires=["gdata>=2.0.9,<=2.0.14"],
      author='${AUTHOR}',
      author_email='${AUTHOR_EMAIL}',
      maintainer='${AUTHOR}',
      maintainer_email='${AUTHOR_EMAIL}',
      url='${PROJECT_URL}',
      download_url='${SITE_URL}',
      description='${SUMMARY}',
      long_description='${DESCRIPTION}',
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

