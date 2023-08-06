Utility functions and classes (``utils``)
=========================================
This module contains functions and classes useful to manipulate input data
(e.g. gene expressions, labels), create outputs and collect results.

.. testsetup:: *

   from l1l2signature.utils import *

.. module:: l1l2signature.utils

Data and parameters
-------------------
.. autoexception:: L1L2SignatureException
.. autoclass:: BioDataReader
.. autoclass:: RangesScaler
   :members:


Results analysis
----------------
.. autofunction:: ordered_submatrices
.. autofunction:: signatures
.. autofunction:: selection_summary
.. autofunction:: confusion_matrix
.. autofunction:: classification_measures


Plotting functions (``plots``)
==============================
This module contains all the utilities used to plot useful results.

.. testsetup:: *

   from l1l2signature.plots import *

.. module:: l1l2signature.plots

.. autofunction:: kfold_errors
.. autofunction:: errors_boxplot
.. autofunction:: heatmap
.. autofunction:: pca
.. autofunction:: selected_over_threshold
