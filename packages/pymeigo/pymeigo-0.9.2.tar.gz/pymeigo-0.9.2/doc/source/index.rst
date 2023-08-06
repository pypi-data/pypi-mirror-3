

#############################
PYMEIGO documentation
#############################

Overview and Installation
##############################

`pymeigo <http://pypi.python.org/pypi/pymeigo>`_  is a python package that provides a python interface to the optimisation tool MEIGOR, which
is a R package available at http://www.iim.csic.es/~gingproc/meigo.html. The original R package provides a scatter search optimisation that is dedicated to the optimisation of R functions. **pymeigo** provides an easy way to use MEIGOR within python so as to optimise python functions as well.


.. note:: for now, pymeigo and MEIGOR have the essR optimisation method only. In
   the close future, VNS method will also be provided. 


.. _installation:

Installation
===============

First, you need to install the MEIGOR package. Please see `MEIGOR page <http://www.iim.csic.es/~gingproc/meigo.html>`_ for up-to-date version or
`CellNOpt page <http://www.ebi.ac.uk/saezrodriguez/cno/downloads.html>`_. For instance, under Linux, type::

    wget http://www.ebi.ac.uk/saezrodriguez/cno/downloads/MEIGOR_0.99.1_svn2071.tar.gz; 
    R CMD INSTALL MEIGOR_0.99.1_svn2071.tar.gz


For **pymeigo** itself, you will need to install `Python <http://www.python.org/download/>`_ (linux and mac users should have it installed already). 

We recommend also to install `ipython <http://ipython.org/>`_, which provides a more flexible shell alternative to the
python shell itself.

Then, since **pymeigo** is available on `PyPi <http://pypi.python.org/>`_, the following command should install **pymeigo** and its dependencies automatically:: 

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
