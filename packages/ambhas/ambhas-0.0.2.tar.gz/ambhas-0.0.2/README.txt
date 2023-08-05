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
  
Changelog
=========

0.0.0 (July 2011)
------------------
- Initial release


Any questions/comments
=========================
If you have any comment/suggestion/question, 
please feel free to write me at satkumartomer@gmail.com

So far, the documents are not well explained, 
I will be updating them soon.




