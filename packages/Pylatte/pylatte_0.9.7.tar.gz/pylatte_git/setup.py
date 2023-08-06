'''
Created on 2012. 8. 4.

@author: HwanSeung Lee(rucifer1217@gmail.com)
'''
from distutils.core import setup, Extension

classifierList=['Development Status :: 4 - Beta',
                'Environment :: Console',
                'License :: OSI Approved :: GNU General Public License (GPL)',
                'Programming Language :: Python :: 3.2',
                'Topic :: Internet :: WWW/HTTP :: HTTP Servers']

setup(name='Pylatte',
      author='HwanSeung lee',
      author_email='rucifer1217@gmail.com',
      description='python Web Framework - pylatte',
      license = "GPL",
      keywords = "webserver Framework",
      url='http://pylatte.org',
      version='0.9.7',
      classifiers = classifierList,
      packages=['Pylatte','Pylatte.Database','Pylatte.WebServer']
)
