# -*- coding: utf-8 -*-
__revision__ = "$Id: setup.py 2065 2012-08-13 10:14:33Z cokelaer $"
import sys
import os
from setuptools import setup, find_packages
import glob


_MAJOR               = 0
_MINOR               = 9
_MICRO               = 0
version              = '%d.%d.%d' % (_MAJOR, _MINOR, _MICRO)
release              = '%d.%d' % (_MAJOR, _MINOR)

metainfo = {
    'authors': {
        'Cokelaer':('Thomas Cokelaer','cokelaer@ebi.ac.uk'),
        },
    'version': version,
    'license' : 'GPL',
    'download_url' : ['http://pypi.python.org/pypi/cnolab.wrapper'],
    'url' : ['http://www.ebi.ac.uk/~cokelaer/cnolab/wrapper'],
    'description':'CellNOpt R packages wrapper and utilities' ,
    'platforms' : ['Linux', 'Unix', 'MacOsX', 'Windows'],
    'keywords' : ['Graph Theory', 'Genetic Algorithm', 'Cell Theory',
        'Signalling Pathways', 'CellNOpt', 'rpy2', 'cno'],
    'classifiers' : [
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.7',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Scientific/Engineering :: Bio-Informatics',
          'Topic :: Scientific/Engineering :: Information Analysis',
          'Topic :: Scientific/Engineering :: Mathematics',
          'Topic :: Scientific/Engineering :: Physics']
    }



setup(
    name             = 'pymeigo',
    version          = version,
    maintainer       = metainfo['authors']['Cokelaer'][0],
    maintainer_email = metainfo['authors']['Cokelaer'][1],
    author           = metainfo['authors']['Cokelaer'][0],
    author_email     = metainfo['authors']['Cokelaer'][1],
    long_description = open("README.txt").read(),
    keywords         = metainfo['keywords'],
    description = metainfo['description'],
    license          = metainfo['license'],
    platforms        = metainfo['platforms'],
    url              = metainfo['url'],      
    download_url     = metainfo['download_url'],
    classifiers      = metainfo['classifiers'],

    # package installation
    package_dir = {'':'src'},
    packages = ['pymeigo'],
    #package_dir  = package_dir,
    install_requires = ['rpy2', 'cnolab.deploy', 'cnolab.wrapper'],
    )


