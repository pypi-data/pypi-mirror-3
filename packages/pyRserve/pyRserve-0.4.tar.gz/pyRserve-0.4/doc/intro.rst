pyRserve
=========

What It Does
-------------

pyRerve is a library for connecting Python to an `R process <http://www.r-project.org/>`_ (an excellent statistic package) running `Rserve <http://www.rforge.net/Rserve/>`_ as a RPC connection gateway. Through such a connection variables can be get and set in R from Python, and also R-functions can be called remotely.  In contrast to `rpy or rpy2 <http://rpy.sourceforge.net/>`_ the R process does not have to run on the same machine, it can run on a remote machine and all variable  access and function calls will be delegated there through the network.

Furthermore - and this makes everything feel very pythonic - all data structures will automatically be converted from native 
R to native Python types and back.


Changes
----------------
* V 0.4 (2011-09-20)
    * Added support for nested function calls. E.g. conn.r.t.test( ....) now works.
    * Proper support for boolean variables and vectors

* V 0.3 (2010-06-08)
    * Added conversion of more complex R structures into Python
    * Updated documentation (installation, manual)
    
* V 0.2 (2010-03-19) Fixed rendering of TaggedArrays

* V 0.1 (2010-01-10) Initial version


Supported Platforms
----------------------------

This package has been mainly developed under Linux, and hence should run on all standard unix platforms. It has also been
successfully used on Win32 machines. Unittests have only been used on the Linux side, however they might just work 
fine for Win32.

It has been tested run with Python 2.6.x and 2.7.x. Python 3.x has never been tested, it might or might not work.

The latest development has been tested with R 2.13.1 and Rserve 0.6.6.

License
-------

pyRserve has been written by `Ralph Heinkel (www.ralph-heinkel.com) <http://www.ralph-heinkel.com/>`_ and is released under `MIT license <http://packages.python.org/pyRserve/license.html>`_.


Quick Installation
-------------------
Make sure that Numpy is installed.

Then from your unix/windows command line run::

    easy_install pyRserve
   
or download the tar.gz or zip package. After unpacking run `python setup.py install` from your command line. 


Full Documentation
------------------

Documentation can be found at `<http://packages.python.org/pyRserve/>`_.

