============
ambhas
============

This is a package/library in python developed under the project `AMBHAS <http://www.ambhas.com/>`_.
This has various module like: copula, errlib etc.


Installing ambhas
======================

Installing ambhas can be done by downloading source file (ambhas--<version>.tar.gz),
and after unpacking issuing the command::

    python setup.py install

This requires the usual Distutils options available.

Or, download the ambhas--<version>.tar.gz file and issue the command::
    
   pip install /path/to/ambhas--<version>.tar.gz

Or, directly using the pip::

   pip install ambhas   


Usage
=========
Import required modules::

    import numpy as np
    from ambhas.errlib import rmse, correlation

Generate some random numbers::

    x = np.random.normal(size=100)
    y = np.random.normal(size=100)
    rmse(x,y)
    correlation(x,y)

For using the copula, import copula::

    import numpy as np
    from ambhas.copula import Copula

Generate some random numbers::

    x = np.random.normal(size=100)
    y = np.random.normal(size=100)

Generate an instance of class copula::

    foo = Copula(x, y, 'frank')

Now, generate some ensemble using this instance::

    u,v = foo.generate(100)

  
Changelog
=========

0.0.0 (July 2011)
------------------
- Initial release

0.0.1 (Nov 2011)
------------------
- a new sublibrary 'krig' added

0.0.2 (Nov 2011)
-----------------
- a new sublibrary 'sunlib' added

0.0.3 (Nov 2011)
-----------------
- A new sub-library added to deal with reading and writting the xls data. This library is based on 'xlrd' and 'xlwt', and provide an easier way to read and write the data.

0.0.4 (Nov 2011)
------------------
- A new sub-library added for a simple groundwater model

Documentation
================
Examples of using this library are provided in the book, 'Python in Hydrology' by Sat Kumar Tomer. 
The books is available for free to download from the website of `AMBHAS <http://www.ambhas.com/>`_. 

Any questions/comments
=========================
If you have any comment/suggestion/question, 
please feel free to write me at satkumartomer@gmail.com





