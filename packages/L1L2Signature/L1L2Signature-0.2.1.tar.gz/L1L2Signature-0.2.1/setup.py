#!/usr/bin/env python
# L1L2Signature setup script

from distutils.core import setup

# Package Version
from l1l2signature import __version__ as version

setup(
    name='L1L2Signature',
    version=version,
    
    description=('Unbiased framework for gene expression analysis'),
    long_description=open('README').read(),
    author='L1L2Signature developers - SlipGURU',
    author_email='slipguru@disi.unige.it',
    maintainer='Salvatore Masecchia',
    maintainer_email='salvatore.masecchia@disi.unige.it',
    url='http://slipguru.disi.unige.it/Software/L1L2Signature/',
    
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'License :: OSI Approved :: BSD License',
        'Topic :: Software Development',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Operating System :: MacOS'
    ],
    license = 'new BSD',

    packages=['l1l2signature'],
    requires=['l1l2py (>=1.4.0)',
              'pplus (>=0.5.1)'],
    scripts=['scripts/l1l2_run.py', 'scripts/l1l2_analysis.py',
             'scripts/l1l2_tau_choice.py']
)