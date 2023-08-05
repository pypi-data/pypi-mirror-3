.. _tutorial:

Quick start tutorial
====================
Assuming `L1L2Py <http://slipguru.disi.unige.it/Software/L1L2Py>`_ and
`PPlus <http://slipguru.disi.unige.it/Software/PPlus>`_ already installed,
**L1L2Signature** may be installed using standard Python tools (with
administrative or sudo permissions on GNU-Linux platforms)::

    $ pip install L1L2Signature

    or

    $ easy_install L1L2Signature


Installation from sources
-------------------------
If you like to manually install **L1L2Signature**, download the source tar.gz
from our
`BitBucket repository <https://bitbucket.org/slipguru/l1l2signature/downloads>`_.
Then extract it and move into the root directory::

    $ tar xvf L1L2Signature-|release|.tar.gz
    $ cd L1L2Signature-|release|/

From here, you may use the standard Python installation step::

    $ python setup.py install

.. note::
    If you would like to use **L1L2Signature** in a distributed environment
    you need to install ``L1L2Py`` and ``PPlus`` on each node, as described
    into the documentation of both libraries.
    You can also run **L1L2Signature** script on a single machine (installing
    dependencies only there) using ``PPlus`` debug mode, configurable from
    **L1L2Signature** configuration file, as described below.


After **L1L2Signature** installation, you should have access to three scripts,
named with a common ``l1l2_`` prefix::

    $ l1l2_<TAB>
    l1l2_analysis.py    l1l2_run.py    l1l2_tau_choice.py

This tutorial assumes that you downloaded and extracted **L1L2Signature**
source package which contains a ``Golub99_Leukemia`` directory with
`Test data <http://www.broadinstitute.org/cgi-bin/cancer/publications/pub_paper.cgi?paper_id=43>`_,
which will be used to show **L1L2Signature**'s tools functionalities.

**L1L2Signature** needs only 3 ingredients:

* A ``gene expressions`` matrix
* A set of ``labels`` for each sample (e.g. phenotype)
* A ``configuration`` file


Input data format
-----------------
Input data (gene expression matrix and labels) are assumed to be textual ad
separated by a char (delimiter).
For example, the given data matrix (of Leukemia gene expressions) is a text file
where samples are organized by columns and microarray probes by row and gene
expressions values are separated by a comma (``','``).

.. literalinclude:: ../Golub99_Leukemia/data/gedm.csv
   :lines: 1, 150-160
   :append: ...

Labels contains information about the given samples, indicated if they belong
to the ALL (Acute Lymphoblastic Leukemia) or AML (Acute Myeloid Leukemia) group:

.. literalinclude:: ../Golub99_Leukemia/data/labels.csv
   :lines: 1-6, 29-34
   :append: ...

See also :class:`l1l2signature.utils.BioDataReader` API and next section for
more information.


.. _configuration:

Configuration File
------------------
**L1L2Signature** configuration file is a standard Python script. It is
imported as a module, then all the code is executed. Actually all configuration
option are mandatory and it is possible to generate a default configuration
file, as the one that follows, with the ``l1l2_run.py`` script
(see :ref:`experiment` section):

.. literalinclude:: ../l1l2signature/config.py
   :language: python

Configuration file is fully documented and it imports ``L1L2Py`` in order to use
some useful tools. User is free to use personalized functions if they follow
the same API. For example, if the user would like to use a different error
function, this must be written as::

    def my_error(true_labels, predicted_labels):
        something(...)
        return error_as_float

After the user defines all the option needed to read the data and to perform the
model assessment, the crucial phase is to properly define  a set of
ranges of parameter involved, namely :math:`\tau`, :math:`\mu` and
:math:`\lambda` (see ``L1L2Py`` for a complete explanation of them).
Usually, a good option for :math:`\lambda` is to use a wide range of values in
geometric series.

Instead, for :math:`\tau` we automatically scale the range respect to the
maximum value (``MAX_TAU``) it can assume. Values greater than ``MAX_TAU``
produce empty models (no genes are selected). Actually, the ``tau_range``
option is considered as relative with respect to ``MAX_TAU``.

About :math:`\mu`, we implemented an heuristic which follows the same criteria
implemented for :math:`\tau`. Because :math:`\mu` is related to the amount of
correlation we would like to introduce into the generated signatures, we would
like to use relative values with respect to each split (sub)matrix.
So, we evaluate a ``CORRELATION_FACTOR``, used as scaling factor, which is
based on the spectral properties of the correlation (sub)matrix.


.. _tau_choice:

Tau choice helper
-----------------
In order to help users choosing a good *relative* :math:`\tau` range, they can
use the ``l1l2_tau_choice.py`` script which has the following prototype::

    $ l1l2_tau_choice.py --help
    Usage: l1l2_tau_choice.py [-s] configuration-file.py

    Options:
      --version   show program's version number and exit
      -h, --help  show this help message and exit
      -s, --show  show interactive plot

It needs a properly configured configuration file, with an *initial* tau range
and performs the following steps:

* Reads data
* Checks ``MAX_TAU`` value (it must select at least 1 variable)
* Calculates a full path of :math:`\ell_1\ell_2` solutions using the
  given :math:`\tau` range (and a :math:`\mu` very close to zero).
  User may check minimum and maximum number of selected variables,
  estimating minimal (without correlation) gene signatures lengths.
* Performs a 5-fold cross validation saving a ``tau_choice_plot.png`` (as the one
  in the next Figure) into the configuration file directory.
  User can estimate a basic (and maybe biased) performance with the given
  ranges of values.

.. figure:: _static/tau_choice_plot.png
   :align: center

   **Tau choice plot for Golub dataset with a default configuration file**


Usually we perform this step many times in order to drive our parameters ranges
choice, before launching the real experiment (which usually requires many hours).


.. _experiment:

Experiment runner
-----------------
The ``l1l2_run.py`` script, executes the full framework described
in the :ref:`overview` section. The prototype is the following::

    $ l1l2_run.py --help
    Usage: l1l2_run.py [-c] configuration-file.py

    Options:
      --version     show program's version number and exit
      -h, --help    show this help message and exit
      -c, --create  create config file

As described before, this script may be also used to generate a valid default
configuration file (``-c`` option).

When launched, the script reads and splits the data, then it runs ``L1L2Py``
on each external split and collects the results in a new sub-directory of the
``result_path`` directory (see :ref:`configuration`). Such a directory is
named as::

    l1l2_result_<TIMESTAMP>

and it contains all information needed for the following analysis step.

.. note::
    Note that data and configuration file are *hard-linked* inside the result
    directory which, in that way, becomes completely portable and self
    contained.


.. _analysis:

Results analysis
----------------
This is the last step, needed to be performed in order to get some useful
summaries and plots from an already executed experiment.
The ``l1l2_analysis.py`` script accepts as only parameter a result directory
already created::

    $ l1l2_analysis.py --help
    Usage: l1l2_analysis.py result-dir

    Options:
      --version   show program's version number and exit
      -h, --help  show this help message and exit
      -d DPI, --dpi=DPI  figures dpi resolution (default 300)
      -s, --show         show interactive plots

The script prints some results and produces a set of textual and graphical
results.

.. _cverrors:

Cross Validation Errors
~~~~~~~~~~~~~~~~~~~~~~~
The script generates a list of ``kcv_err_split_*.png``, one for each external
split (as averaged error across internal splits). Moreover, it generates an
averaged plot: ``avg_kcv_err.png``.
On each plot, a blue dot indicates the minimum.

.. figure:: _static/avg_kcv_err.png
   :align: center

   **Averaged Cross Validation Error for Golub dataset with a default
   configuration file**

See also: :func:`l1l2signature.plots.kfold_errors`.

.. _boxplots:

Prediction Errors
~~~~~~~~~~~~~~~~~
The script generates a box plot for both test and training errors, respectively
``prediction_error_ts.png`` and ``prediction_error_tr.png``.
They show the averaged prediction error over external splits in order to asses
performance and stability of the signatures (for each level of considered
correlation, :math:`\mu` values).

.. figure:: _static/prediction_error_ts.png
   :align: center

   **Prediction Error Box Plot for Golub dataset with a default
   configuration file**

See also: :func:`l1l2signature.plots.errors_boxplot`.

Frequencies Threshold
~~~~~~~~~~~~~~~~~~~~~
In order to help the user defining a good stability threshold (see
``frequency_threshold`` in :ref:`configuration`) the script also plots
(and actually print and save as ``selected_over_threshold.png``), an overall
summary of the number of genes selected for different thresholds and for
each correlation level.

.. figure:: _static/selected_over_threshold.png
   :align: center

   **Number of selected variables wrt a frequency (stability) threshold over
   external split signatures (Golub dataset)**

See also: :func:`l1l2signature.plots.selected_over_threshold` and
:func:`l1l2signature.utils.selection_summary`.


.. _heatmaps:

Signatures Heatmaps
~~~~~~~~~~~~~~~~~~~
In case of classification (automatically identified when labels assume only
two values), the script creates a heatmap plot for each final signature (then
they also depend by ``frequency_threshold`` option value). Images are saved as
``heatmap_mu*.png`` files where samples and variables are
**properly clustered** in order to improve the visualization.

.. figure:: _static/heatmap_mu1.png
   :align: center

   **Heatmap for Golub dataset with a default configuration file**

See also: :func:`l1l2signature.plots.heatmap` and
:func:`l1l2signature.utils.ordered_submatrices`.

Samples in PCA space
~~~~~~~~~~~~~~~~~~~~
In case of classification (automatically identified when labels assume only
two values), the script plots samples in a 3D space, using Principal Component
Analysis (PCA), for each final signature. Images are saved as
``pca_mu*.png`` files.

.. figure:: _static/pca_mu1.png
   :align: center

   **PCA plot for Golub dataset with a default configuration file**

See also: :func:`l1l2signature.plots.pca`.

.. warning::
    Note that this function may lead to memory issues if the selected variables
    (depending on ``frequency_threshold``) or the number of samples is too high.

Performance Statistics
~~~~~~~~~~~~~~~~~~~~~~
The analysis script also produces some textual results, saved into a
``stats.txt`` file. That file is divided into some sections, each one
containing at least a short table.

Optimal Parameters
^^^^^^^^^^^^^^^^^^
.. literalinclude:: _static/stats.txt
   :lines: 5-12

This table describes the best parameter pairs :math:`(\lambda^*, \tau^*)` found
in each cross validation split. They correspond to blue points in generated
:ref:`cverrors` images.

Prediction errors
^^^^^^^^^^^^^^^^^
.. literalinclude:: _static/stats.txt
   :lines: 15-38

These tables show the averaged prediction error of the signatures, before
frequency/stability thresholding, for each value of correlation :math:`\mu`.
They correspond to the generated :ref:`boxplots` box plots.

Classification Performances
^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. literalinclude:: _static/stats.txt
   :lines: 91-99

This table, generated only in classification for each :math:`\mu`,
summarizes classification performances of the signature. It is a classical
*Confusion Matrix* where, e.g. the entry AML vs ALL indicates the number of
real AML samples classified as belonging to ALL class (results generate on
given Golub "Leukemia" dataset).
On the bottom we have *True rates*:
``#(Correctly predicted as C) / #(Predicted as C)``
while on the right we have *Predictive values*:
``#(Correctly predicted as C) / #(Samples in C)``

Moreover, this section contains some other performance measures:

.. literalinclude:: _static/stats.txt
   :lines: 102-105

where, MCC is the *Matthews correlation coefficient*.

At last, if the ``positive_label`` parameter is given, into
the :ref:`configuration`, the script is able to calculate some other measures
that assume the presence of a *positive class* as in the case of patients
vs. controls. For example, the following table is generated if we assume that
for the "Leukemia" dataset the **AML** class has to be considered as positive:

.. literalinclude:: _static/stats.txt
   :lines: 108-113

Note that some of this measures are pure aliases of the ones already calculated
on the last row or column of the confusion matrix.

See also: :func:`l1l2signature.utils.confusion_matrix` and
:func:`l1l2signature.utils.classification_measures`.

Signatures
~~~~~~~~~~
Obviously, the script generates a set of signatures, each one written in a
separated text file ``signature_mu*.txt``, in order to eventually simplify
the parsing. Each file contains the ordered list of probes belonging to
the signature:

.. literalinclude:: _static/signature_mu1.txt

The file is tab-delimited, the signatures are thresholded with respect to
the ``frequency_threshold`` option, and they correspond to the signatures used
to generate :ref:`Heatmaps plots <heatmaps>`.

See also: :func:`l1l2signature.utils.signatures` and
:func:`l1l2signature.utils.selection_summary`.
