.. _overview:

Framework overview
===================
The main aim of the framework is proposing an unbiased framework for
gene expression analysis. Originally this framework was designed by combining
a gene selection core with a significance assessment step [Barla08]_.
Even if we currently use both step in our experiments (see :ref:`applications`),
actually **L1L2Signature** implements the latter only partially (permutation
tests still missing).

In the context of detecting significant molecular alterations by gene
expression profiling a main goal, besides classification, is finding a
gene signature, that is a panel of genes able to discriminate between two
given classes e.g. patients and controls.

Such an analysis encompasses at least two steps, gene selection and
model assessment.
The gene selection step, is based on elastic net regularization where we
explicitly take into account regularization parameter tuning.
That core, described and presented in [DeMol09]_, is nested into a general
architecture to assess the statistical significance of the model via
cross validation.

When dealing with high-throughput data the choice of a consistent selection
algorithm is not sufficient to guarantee good results. It is therefore
essential to introduce a robust methodology to select the significant
variables not susceptible of selection bias [Ambroise02]_.

**L1L2Signature** is a a framework based on two nested loops:
    * the internal one is responsible for **model selection** and is based
      on a cross validation strategy;
    * the external loop is for **model assessment**.

Model (gene) selection
----------------------
A good algorithm should take into account at least linear interaction of
multiple genes.
Standard statistical (univariate) approaches take into consideration one gene
at the time and then rank them according to their fold-change or to their
prediction power. Indeed in most cases a multivariate model is preferable.

Another drawback of many variable selection algorithms is the rejection of
part of the relevant genes due to redundancy. In many biological studies some
of the input variables may be highly correlated with each other.
As a consequence, when one variable is considered relevant to the problem,
its correlated variables should be considered relevant as well.

Given the above premises we focused on the elastic net selection method
as presented in [DeMol09]_.

.. image:: _static/nested_lists.png
   :align: center
   :alt: Gene selection core generating (almost) nested lists of genes.

Model assessment
----------------
The gene selection step is nested in an external cross validation loop, needed
to verify the goodness of the estimated model both in terms of performance
stability and significance.

In order to obtain an unbiased estimate of the classification performance
[Ambroise02]_, this step must be carefully designed by holding out a blind
test set.
Since the available samples are very few compared to the number of variables,
this step has to be performed on different subsamplings and its results
averaged.

.. image:: _static/full_fw.png
   :align: center


.. rubric:: References

.. [Ambroise02] ﻿Ambroise C., McLachlan G. J.,
                **Selection bias in gene extraction on the basis of microarray
                gene-expression data**.
                Proceedings of the National Academy of Sciences of the
                United States of America, 99(10), 6562-6, 2002
.. [Barla08]    Barla A., Mosci S., Rosasco L., Verri A.,
                **A method for robust variable selection with significance
                assessment**.
                European Symposium on Artificial Neural Networks, 2008
.. [DeMol09]    De Mol C., Mosci S., Traskine M., Verri A.,
                **A Regularized Method for Selecting Nested Group of Genes from
                Microarray Data**.
                Journal of Computational Biology, vol. 16, pp. 677-690, 2009.


.. _applications:

Framework Applications
======================
Such a framework (in a previous Matlab implementation or in the implementation
here described), was used in many biological application:

*  Barla A., Jurman G., Visintainer R., Squillario M., Filosi M.,
   Riccadonna S. and Furlanello C.,
   **A machine learning pipeline for discriminant pathways identification**.
   Proceedings CIBB 2011.

* Zycinski G., Barla A. and Verri A.,
  **SVS: Data and knowledge integration in computational biology**.
  Proceedings of IEEE EMBC 2011, 2011.

* Squillario M. and Barla A.,
  **A computational procedure for functional characterization of potential
  marker genes from molecular data: Alzheimer's as a case study**.
  BMC Medical Genomics, 4 (55) , 2011.

* Fardin P., Cornero A., Barla A., Mosci S., Acquaviva M., Rosasco L.,
  Gambini C., Verri A. and Varesio L.,
  **Identification of multiple hypoxia signatures in neuroblastoma cell lines
  by l1-l2 regularization and data reduction**.
  Journal of Biomedicine and Biotechnology, 2010.

* Fardin P., Barla A., Mosci S., Rosasco L., Verri A., Versteeg R., Caron H.,
  Molenaar J., Ora I., Eva A., Puppo M. and Varesio L.,
  **A biology-driven approach identifies the hypoxia gene signature as a
  predictor of the outcome of neuroblastoma patients**.
  Molecular Cancer, 2010.

* Fardin P., Barla A., Mosci S., Rosasco L., Verri A. and Varesio L.,
  **The l1-l2 regularization framework unmasks the hypoxia signature hidden in
  the transcriptome of a set of heterogeneous neuroblastoma cell lines**.
  BMC Genomics, 10 , pp.474, 2009.

* Mosci S., Barla A., Verri A. and Rosasco L.,
  **Finding structured gene signatures**.
  IEEE Proceedings BIBM 2008, pp.8, 2008
