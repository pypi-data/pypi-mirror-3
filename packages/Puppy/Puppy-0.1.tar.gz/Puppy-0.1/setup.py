RELEASE = True

from setuptools import setup, find_packages
import sys, os

classifiers = """\
Development Status :: 5 - Production/Stable
Environment :: Console
Intended Audience :: Developers
Intended Audience :: Science/Research
License :: OSI Approved :: MIT License
Operating System :: OS Independent
Programming Language :: Python
Topic :: Scientific/Engineering
Topic :: Software Development :: Libraries :: Python Modules
"""

version = '0.1'

setup(
        name='Puppy',
        version=version,
        description="DSL for creating NetCDF files",
        long_description="""\
A DSL for creating NetCDF files. Here's a simple example::

.. code-block:: python

    from pup import *

    class Test(NetCDF):
        history = 'Created for a test'
        time = Variable(range(10), units='days since 2008-01-01')

    Test.save('simple.nc')

By default it uses pupynere for creating files, but this can be overloaded::

.. code-block:: python

    from pynetcdf import netcdf_file

    class Test(NetCDF):
        loader = netcdf_file
        ...

A more complex example::

.. code-block:: python

    from pup import *

    # t1, lon, lat and runoff must be defined before

    class Runoff(NetCDF):
        TIME = Variable(t1.astype('d'), record=True, 
                long_name='time', 
                units=units, 
                time_origin='01-JAN-1900 00:00:00', 
                axis='T', cartesian_axis='T', 
                calendar_type='JULIAN')

        grid_x_T = Variable(lon,
                long_name='Nominal Longitude of T-cell center',
                axis='X',
                units='degrees_east')

        grid_y_T = Variable(lat,
                long_name='Nominal Latitude of T-cell center',
                axis='Y',
                units='degrees_north')

        RUNOFF = Variable(runoff, (TIME, grid_y_T, grid_x_T),
                long_name='water flux: runoff',
                missing_value=f1.variables['FLOW']._FillValue,
                units='(kg/s)/m^2')

    Runoff.save('RUNOFF_interannual.nc')

""",
        classifiers=filter(None, classifiers.split("\n")),
        keywords='netcdf data array math',
        author='Roberto De Almeida',
        author_email='roberto@dealmeida.net',
        #url='http://bitbucket.org/robertodealmeida/pupynere/',
        #download_url = "http://cheeseshop.python.org/packages/source/p/pupynere/pupynere-%s.tar.gz" % version,
        license='MIT',
        py_modules=['pup'],
        include_package_data=True,
        zip_safe=True,
        test_suite = 'nose.collector',
        install_requires=[
            'numpy',
        ],
        extras_require={
            'test': ['nose'],
        },
)
