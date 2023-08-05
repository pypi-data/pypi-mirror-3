===========================================================
L1L2Signature - Unbiased framework for -omics data analysis
===========================================================

:Release: |release|
:Homepage: http://slipguru.disi.unige.it/Software/L1L2Signature
:Repository: https://bitbucket.org/slipguru/l1l2signature

**L1L2Signature** is an implementation of an unbiased framework originally
thought for gene expression analysis.
The need of such a framework may be found in the :ref:`overview` section
illustrating the dramatic effect of a biased approach especially when the
sample size is small.

The framework, here implemented, was used in many real applications and a
collection of them is referenced in the :ref:`applications` section.

This library is composed by a set of Python scripts (described
in the :ref:`tutorial`) and a set of useful classes and functions (described in
the :ref:`api` section) that could be used to manually read and/or analyze
high-throughput data extending/integrating the proposed pipeline.

**L1L2Signature** relies on two libraries also implemented by our research
group and already released as open source libraries:

    * `L1L2Py <http://slipguru.disi.unige.it/Software/L1L2Py>`_:
      implements the gene selection core, based on *elastic net* regularization.
    * `PPlus <http://slipguru.disi.unige.it/Software/PPlus>`_: used to
      parallelize cross validation splits in an easy and effective way across
      a set of desktop personal computer distributed in our labs.


User documentation
==================
.. toctree::
   :maxdepth: 2

   description.rst
   tutorial.rst


.. _api:

Public API
==========
.. toctree::
   :maxdepth: 1

   api.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
