from distutils.core import setup

setup(name="PyThorlabsMDT",
      version='1.0',
      description='Module to drive the Thorlabs MDT693A piezo controller',
      author='Pierre Clade, Anatole Julian & Nicolas Campagnolle', 
      author_email="pierre.clade@spectro.jussieu.fr",
      maintainer='Pierre Clade',
      maintainer_email="pierre.clade@spectro.jussieu.fr",
      url='http://packages.python.org/PyThorlabsMDT/',
      license='''\
This software can be used under one of the following two licenses: \
(1) The BSD license. \
(2) Any other license, as long as it is obtained from the original \
author.''',


      long_description='''\
Overview
========
      
This package can be used to drive the Thorlabs MDT693A piezo controller.

This package has been tested on  Windows and Linux.


Example
-------
::

    import PyThorlabsMDT
    pzt = PyThorlabsMDT.PZT_driver'port='COM2'
    pzt.x = 45 # set the x-axis to 45 V
    pzt.set_x(45) #equivalent to the command above 
    print pzt.x # Display the value of the x-axis
    pzt.get_info() #Display the informations about the device

Installation
============

You need first to check if the serial backends for Python (package pySerial)
    ===>  http://pyserial.sourceforge.net/


To install PyThorlabsMDT, download the package and run the command::

    python setup.py install


''',  
      keywords=['MDT693A', 'Thorlabs', 'Piezo controller','3-axis'],      
      requires='serial',
        classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules'],
     
      py_modules = ['PyThorlabsMDT'],
      
      
      )
