

#############################
PYMEIGO documentation
#############################

Overview and Installation
##############################

**pymeigo** is a python package that provides a python interface to the optimisation tool MEIGOR, which
is a R package available at http://www.iim.csic.es/~gingproc/meigo.html. The original R package provides a scatter search optimisation that is obviously dedicated to the optimisation of R functions. **pymeigo** provides an easy way to use MEIGOR within python so as to optimise python functions as well.


.. _installation:

Installation
===============
First, you will need to install `Python <http://www.python.org/download/>`_
(linux and mac users should have it installed already). 

We recommend also to install `ipython <http://ipython.org/>`_, which provides a more flexible shell alternative to the
python shell itself.

**pymeigo** depends on **cnolab.wrapper** that provides some convenient tools to wrap R packages in python. 

Since **pymeigo** and **cnolab.wrapper** are available on `PyPi <http://pypi.python.org/>`_, the following command should install **pymeigo** and its dependencies automatically:: 

    easy_install pymeigo

or::

    pip pymeigo


.. note:: to use *easy_install* or *pip* you may need root permission (under linux, use *sudo*)


User guide
##################


.. toctree::
    :maxdepth: 2
    :numbered:

    quickstart.rst


References
##################


.. toctree::
    :maxdepth: 2
    :numbered:

    references


Citations
################

If you use essR and publish the results, please cite the following papers: 

#. Egea, J.A., Maria, R., Banga, J.R. (2010) An evolutionary method for complex-process optimization. Computers & Operations Research 37(2): 315-324. 
#. Egea, J.A., Balsa-Canto, E., Garcia, M.S.G., Banga, J.R. (2009) Dynamic optimization of nonlinear processes with an enhanced scatter search method. Industrial & Engineering Chemistry Research 49(9): 4388-4401.
