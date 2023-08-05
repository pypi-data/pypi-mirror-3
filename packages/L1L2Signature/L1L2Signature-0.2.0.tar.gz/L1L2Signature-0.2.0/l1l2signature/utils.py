"""Utilities functions and classes."""

# Author: Salvatore Masecchia <salvatore.masecchia@disi.unige.it>,
#         Annalisa Barla <annalisa.barla@disi.unige.it>
# License: new BSD.

import l1l2py
import numpy as np


class L1L2SignatureException(Exception):
    """Exception raised by ``L1L2Signature`` classes and functions."""
    pass


class BioDataReader(object):
    """Biological Data reader.

    This class reads a pair of CSV files containing respectively a
    data matrix and a list of labels.

    The reader can discard some samples and some variables according to
    give arguments (as described below) and assumes the presence
    of an header line in both files.

    If labels file contains exactly 2 labels, `BioDataReader`
    automatically maps two classes in -1 and +1. Then, the `labels_reverse`
    attribute will contain a dictionary mapping from numeric to string labels
    (otherwise it is None).
    Otherwise `BioDataReader` assumes to find numeric values (regression
    task).

    Parameters
    ----------
    data_file : file or str
        File, filename, or generator to read (see also :func:`numpy.loadtxt`)
    labels_file : file or str
        File, filename, or generator to read (see also :func:`numpy.loadtxt`)
    variable_remover : int or None, optional (default None)
        Variable names prefix used to discard samples
        (e.g. ``AFFX`` for Affymetrix Gene Expression MicroArray)
    sample_remover : str or None, optional (default None)
        Label value used to discard samples prefix. This value must refer to
        the original labels into the labels file.
    delimiter : str, optional (default ',')
        CSV char delimiter (if it is not a comma)
    samples_on : 'col' or 'row', optional (default 'col')
        Indicates if the samples are arranged on rows or columns into the data
        file
    positive_label : str, optional (default None)
        Indicates what label has to be considered as the positive class (mapped
        to +1 value). If None, mapping follows a lexicographic order.

    Attributes
    ----------
    data : :class:`numpy.ndarray`
        Data matrix (``float``) of dimensions ``samples X variables``
    labels : :class:`numpy.ndarray`
        Labels array (``float``)
    samples : :class:`numpy.ndarray`
        Samples names (``str``)
    variables : :class:`numpy.ndarray`
        Variables names (``str``)
    labels_reverse : :class:`dict`
        Mapping from -1 and +1 classes to original string labels.
        The attribute is None if automatic mapping is not performed.

    Examples
    --------
    >>> from l1l2signature.utils import BioDataReader
    >>> from cStringIO import StringIO
    >>> STD_DATA = '\\n'.join(['probe, A,   B,   C,   D',
    ...                       'p1,    0.0, 0.1, 0.2, 0.3',
    ...                       'p2,    0.0, 0.1, 0.2, 0.3',
    ...                       'p3,    0.0, 0.1, 0.2, 0.3',
    ...                       'p4,    0.0, 0.1, 0.2, 0.3',
    ...                       'p5,    0.0, 0.1, 0.2, 0.3'])
    >>> STD_LABELS = '\\n'.join(['name, value',
    ...                         'A,    1',
    ...                         'B,    0',
    ...                         'C,    1',
    ...                         'D,    1'])
    >>> br = BioDataReader(StringIO(STD_DATA), StringIO(STD_LABELS))
    >>> print br.samples
    ['A' 'B' 'C' 'D']
    >>> print br.variables
    ['p1' 'p2' 'p3' 'p4' 'p5']
    >>> print br.data
    [[ 0.   0.   0.   0.   0. ]
     [ 0.1  0.1  0.1  0.1  0.1]
     [ 0.2  0.2  0.2  0.2  0.2]
     [ 0.3  0.3  0.3  0.3  0.3]]
    >>> print br.labels
    [ 1. -1.  1.  1.]
    >>>
    
    """

    def __init__(self, data_file, labels_file,
                 sample_remover=None,
                 variable_remover=None,
                 delimiter=',', samples_on='col', positive_label=None):

        samples_on = samples_on.lower()
        if not samples_on in ('row', 'col'):
            raise L1L2SignatureException("wrong parameter 'samples_on'.")

        # Public attributes
        self.data = None
        self.labels = None
        self.samples = None
        self.variables = None
        self.labels_reverse = None

        self._extract_data(data_file, delimiter, samples_on, variable_remover)
        self._extract_labels(labels_file, delimiter, sample_remover,
                             positive_label)

    def _extract_data(self, data_file, delimiter, samples_on, variable_remover):
        raw_data = np.loadtxt(data_file, dtype='S', delimiter=delimiter)

        self.data = raw_data[1:,1:].astype(np.float)
        self.samples = np.array([x.strip() for x in raw_data[0,1:]])
        self.variables = np.array([x.strip() for x in raw_data[1:,0]])

        if samples_on == 'row':
            self.samples, self.variables =  self.variables, self.samples
        else:
            self.data = self.data.T

        # Discard Variables
        if not variable_remover is None:
            discard_idx = np.array([x.lower().startswith(variable_remover)
                                    for x in self.variables])
            self.data = self.data[:,-discard_idx]
            self.variables = self.variables[-discard_idx]

    def _extract_labels(self, labels_file, delimiter, sample_remover,
                        positive_label):
        raw_labels = np.loadtxt(labels_file, dtype='S', delimiter=delimiter)

        labels_samples = dict((ls.strip(), i)
                                for i, ls in enumerate(raw_labels[1:,0]))
        try:
            order = np.array([labels_samples[ls] for ls in self.samples])
        except KeyError:
            raise L1L2SignatureException('labels mismatch.')

        # Labels management ---
        labels = np.asarray([raw_labels[1:,1][o].strip() for o in order])

        # Filtering is performed before the mapping!
        if not sample_remover is None:
            discard_idx = (labels == str(sample_remover))
            self.samples = self.samples[-discard_idx]
            self.data = self.data[-discard_idx]
            labels = labels[-discard_idx]

        try:
            unique_labels, _, _ = _check_unique_labels(labels)
            self.labels = np.empty_like(labels, dtype=float)

            if not positive_label is None:
                positive_label = str(positive_label)
                if not positive_label in unique_labels:
                    raise L1L2SignatureException('positive label %s not '
                                                 'found.' % positive_label)

                negative_label = np.setdiff1d(unique_labels,
                                              [positive_label])[0]
                self.labels_reverse = {-1.:negative_label, 1.:positive_label}
            else:
                self.labels_reverse = dict(zip((-1., 1.), unique_labels))

            for c, l in self.labels_reverse.iteritems():
                self.labels[labels == l] = c

        except L1L2SignatureException: # more than 2 labels
            try:
                self.labels = labels.astype(np.float) # Regression task
            except ValueError:
                raise L1L2SignatureException('wrong regression labels.')


class RangesScaler(object):
    """Given data and labels helps to scale L1L2 parameters ranges properly.

    This class works on tau and mu ranges passed to the l1l2 selection
    framework (see also :func:`l1l2py.model_selection` and related
    function for details).

    Scaling ranges permits to use relative (and not absolute) ranges of
    parameters.

    Attributes
    ----------
    norm_data : :class:`numpy.ndarray`
        Normalized data matrix.
    norm_labels : :class:`numpy.ndarray`
        Normalized labels vector.
    """
    def __init__(self, data, labels, data_normalizer=None,
                 labels_normalizer=None):

        self.norm_data = data
        self.norm_labels = labels
        self._tsf = self._msf = None

        # Data must be normalized
        if data_normalizer:
            self.norm_data = data_normalizer(self.norm_data)
        if labels_normalizer:
            self.norm_labels = labels_normalizer(self.norm_labels)

    def tau_range(self, trange):
        """Returns a scaled tau range.

        Tau scaling factor is the maximum tau value to avoid and empty solution
        (where all variables are discarded).
        The value is estimated on the maximum correlation between data and
        labels.

        Parameters
        ----------
        trange : :class:`numpy.ndarray`
            Tau range containing relative values (expected maximum is lesser
            than 1.0 and minimum greater than 0.0).

        Returns
        -------
        tau_range : :class:`numpy.ndarray`
            Scaled tau range.
        """
        return np.asanyarray(trange) * self.tau_scaling_factor

    def mu_range(self, mrange):
        """Returns a scaled mu range.

        Mu scaling factor is estimated on the maximum eigenvalue of the
        correlation matrix and is used to simplify the parameters choice.

        Parameters
        ----------
        mrange : :class:`numpy.ndarray`
            Mu range containing relative values (expected maximum is lesser
            than 1.0 and minimum greater than 0.0).

        Returns
        -------
        mu_range : :class:`numpy.ndarray`
            Scaled mu range.
        """
        return np.asanyarray(mrange) * self.mu_scaling_factor

    @property
    def tau_scaling_factor(self):
        """Tau scaling factor calculated on given data and labels."""
        if self._tsf is None:
            self._tsf = self._tau_scaling_factor()
        return self._tsf

    @property
    def mu_scaling_factor(self):
        """Mu scaling factor calculated on given data matrix."""
        if self._msf is None:
            self._msf = self._mu_scaling_factor()
        return self._msf

    def _tau_scaling_factor(self):
        return l1l2py.algorithms.l1_bound(self.norm_data, self.norm_labels)

    def _mu_scaling_factor(self):
        n, d = self.norm_data.shape

        if d > n:
            tmp = np.dot(self.norm_data, self.norm_data.T)
            num = np.linalg.eigvalsh(tmp).max()
        else:
            tmp = np.dot(self.norm_data.T, self.norm_data)
            evals = np.linalg.eigvalsh(tmp)
            num = evals.max() + evals.min()

        return (num/(2.*n))


## Results analysis -----------------------------------------------------------
def ordered_submatrices(data, labels, signatures_idxs):
    """Returns a list of sorted and filtered submatrices.

    The matrices are sorted by ``labels`` and filtered by ``signatures_idxs``.

    Parameters
    ----------
    labels : list
        Data labels
    signatures_idxs : list of :class:`numpy.ndarray`
        Each list item contains a signature in terms of variables
        boolean mask or indexes. If indexes are given, submatrices are also
        properly ordered.

    Returns
    -------
    labels_idxs : :class:`numpy.ndarray`
        Labels ordering used to produce submatrices.
    sub_matrices : list of :class:`numpy.ndarray`
        List of ordered and filtered submatrices.

    Examples
    --------
    >>> from l1l2signature.utils import ordered_submatrices
    >>> data = [[1., 2., 3.],
    ...         [4., 5., 6.],
    ...         [7., 8., 9.]]
    >>> labels = [1, -1, 1]
    >>> signatures_idxs = [[True, False, False],
    ...                    [0, 1, 2],
    ...                    [2, 1]]
    >>> labels_idxs, sub_matrices = ordered_submatrices(data, labels,
    ...                                                 signatures_idxs)
    >>> print labels_idxs
    [1 0 2]
    >>> print sub_matrices[0]
    [[ 4.]
     [ 1.]
     [ 7.]]
    >>> print sub_matrices[1]
    [[ 4.  5.  6.]
     [ 1.  2.  3.]
     [ 7.  8.  9.]]
    >>> print sub_matrices[2]
    [[ 6.  5.]
     [ 3.  2.]
     [ 9.  8.]]
    """
    data = np.asanyarray(data)
    labels = np.asanyarray(labels)

    # Mergesort: stable and efficient when labels are almost already sorted
    labels_idxs = np.argsort(labels, kind='mergesort')

    sub_matrices = list()
    for sig in signatures_idxs:
        sig = np.asanyarray(sig)
        subX = data[:, sig][labels_idxs]
        sub_matrices.append(subX.copy())

    return labels_idxs, sub_matrices


def signatures(splits_results, frequency_threshold=0.0):
    """Returns (almost) nested signatures for each correlation value.

    The function returns 3 lists where each item refers to a signature
    (for increasing value of linear correlation).
    Each signature is orderer from the most to the least selected variable
    across KCV splits results.

    Parameters
    ----------
    splits_results : iterable
        List of results from L1L2Py module, one for each external split.
    frequency_threshold : float
        Only the variables selected more (or equal) than this threshold are
        included into the signature.

    Returns
    -------
    sign_totals : list of :class:`numpy.ndarray`.
        Counts the number of times each variable in the signature is selected.
    sign_freqs : list of :class:`numpy.ndarray`.
        Frequencies calculated from ``sign_totals``.
    sign_idxs : list of :class:`numpy.ndarray`.
        Indexes of the signatures variables .

    Examples
    --------
    >>> from l1l2signature.utils import signatures
    >>> splits_results = [{'selected_list':[[True, False], [True, True]]},
    ...                   {'selected_list':[[True, False], [False, True]]}]
    >>> sign_totals, sign_freqs, sign_idxs = signatures(splits_results)
    >>> print sign_totals
    [array([ 2.,  0.]), array([ 2.,  1.])]
    >>> print sign_freqs
    [array([ 1.,  0.]), array([ 1. ,  0.5])]
    >>> print sign_idxs
    [array([0, 1]), array([1, 0])]
    """
    # Computing totals and frequencies
    selection_totals = selection_summary(splits_results)
    selection_freqs = selection_totals / len(splits_results)

    # Variables are ordered and filtered by frequency threshold
    sorted_idxs = np.argsort(selection_freqs, axis=1)
    sorted_idxs = (sorted_idxs.T)[::-1].T # Reverse order

    # ... ordering
    for i, si in enumerate(sorted_idxs):
        selection_freqs[i] = selection_freqs[i][si]
        selection_totals[i] = selection_totals[i][si]

    # ... filtering
    threshold_mask = (selection_freqs >= frequency_threshold)

    ## Signatures Ordered and Filtered!
    sign_totals = list()
    sign_freqs = list()
    sign_idxs = list()
    for i, mask in enumerate(threshold_mask):
        sign_totals.append(selection_totals[i][mask])
        sign_freqs.append(selection_freqs[i][mask])
        sign_idxs.append(sorted_idxs[i][mask])

    return sign_totals, sign_freqs, sign_idxs


def selection_summary(splits_results):
    """Counts how many times each variables was selected.

    Parameters
    ----------
    splits_results : iterable
        List of results from L1L2Py module, one for each external split.

    Returns
    -------
    summary : :class:`numpy.ndarray`
        Selection summary. ``# mu_values X # variables`` matrix.
    """
    # Sum selection lists by mu values (mu_num x num_var)
    return np.sum(np.asarray(sr['selected_list'], dtype=float)
                     for sr in splits_results)


def confusion_matrix(labels, predictions):
    """Calculates a confusion matrix.

    From given real and predicted labels, the function calculated
    a confusion matrix as a double nested dictionary.
    The external one contains two keys, ``'T'`` and ``'F'``.
    Both internal dictionaries
    contain a key for each class label. Then the ``['T']['C1']`` entry counts
    the number of correctly predicted ``'C1'`` labels,
    while ``['F']['C2']`` the incorrectly predicted ``'C2'`` labels.

    Note that each external dictionary correspond to a confusion
    matrix diagonal and the function works only on two-class labels.

    Parameters
    ----------
    labels : iterable
        Real labels.

    predictions : iterable
        Predicted labels.

    Returns
    -------
    cm : dict
        Dictionary containing the confusion matrix values.
    """
    cm = {'T': dict(), 'F': dict()}

    real_unique_labels, real_C1, real_C2 = _check_unique_labels(labels)
    pred_unique_labels, pred_C1, pred_C2 = _check_unique_labels(predictions)

    if not np.all(real_unique_labels == pred_unique_labels):
        raise L1L2SignatureException('real and predicted labels differ.')

    cm['T'][real_unique_labels[0]] = (real_C1 & pred_C1).sum()  # True C1
    cm['T'][real_unique_labels[1]] = (real_C2 & pred_C2).sum()  # True C2
    cm['F'][real_unique_labels[0]] = (real_C2 & pred_C1).sum()  # False C1
    cm['F'][real_unique_labels[1]] = (real_C1 & pred_C2).sum()  # False C2

    return cm


def classification_measures(confusion_matrix, positive_label=None):
    """Calculates some classification measures.

    Measures are calculated from a given confusion matrix
    (see :func:`confusion_matrix` for a detailed description of the
    required structure).

    The ``positive_label`` arguments allows to specify what label has to be
    considered the positive class. This is needed to calculate some
    measures like F-measure and set some aliases (e.g. precision and recall
    are respectively the 'predictive value' and the 'true rate' for the
    positive class).

    If ``positive_label`` is None, the resulting dictionary will not
    contain all the measures. Assuming to have to classes 'C1' and 'C2',
    and to indicate 'C1' as the positive (P) class, the function returns a
    dictionary with the following structure::

        {
            'C1': {'predictive_value': --,  # TP / (TP + FP)
                   'true_rate':        --}, # TP / (TP + FN)
            'C2': {'predictive_value': --,  # TN / (TN + FN)
                   'true_rate':        --}, # TN / (TN + FP)
            'accuracy':          --,        # (TP + TN) / (TP + FP + FN + TN)
            'balanced_accuracy': --,        # 0.5 * ( (TP / (TP + FN)) +
                                            #         (TN / (TN + FP)) )
            'MCC':               --,        # ( (TP * TN) - (FP * FN) ) /
                                            # sqrt( (TP + FP) * (TP + FN) *
                                            #       (TN + FP) * (TN + FN) )

            # Following, only with positive_labels != None
            'sensitivity':       --,        # P true rate: TP / (TP + FN)
            'specificity':       --,        # N true rate: TN / (TN + FP)
            'precision':         --,        # P predictive value: TP / (TP + FP)
            'recall':            --,        # P true rate: TP / (TP + FN)
            'F_measure':         --         # 2. * ( (Precision * Recall ) /
                                            #        (Precision + Recall) )
        }

    Parameters
    ----------
    confusion_matrix : dict
        Confusion matrix (as the one returned by :func:`confusion_matrix`).

    positive_label : str
        Positive class label.

    Returns
    -------
    summary : dict
        Dictionary containing calculated measures.
    """
    # Confusion Matrix
    #           True P      True N
    # Pred P      TP         FP         P Pred Value
    # Pred N      FN         TN         N Pred Value
    #         Sensitivity Specificity

    labels = confusion_matrix['T'].keys()

    if not positive_label is None:
        P = positive_label
        if not P in labels:
            raise L1L2SignatureException('label %s not found.' % positive_label)

        N = set(labels).difference([positive_label]).pop()
    else:
        P, N = sorted(labels)

    # shortcuts ------------------------------------
    TP = confusion_matrix['T'][P]
    TN = confusion_matrix['T'][N]
    FP = confusion_matrix['F'][P]
    FN = confusion_matrix['F'][N]
    # ----------------------------------------------

    summary = dict({P:dict(), N:dict()})

    summary[P]['predictive_value'] = TP / float(TP + FP)
    summary[P]['true_rate'] = TP / float(TP + FN)           # sensitivity

    summary[N]['predictive_value'] = TN /  float(TN + FN)
    summary[N]['true_rate'] = TN / float(TN + FP)           # specificity

    summary['accuracy'] = (TP + TN) / float(TP + FP + FN + TN)
    summary['balanced_accuracy'] = 0.5 * (summary[P]['true_rate'] +
                                          summary[N]['true_rate'])

    den = ( (TP + FP) * (TP + FN) * (TN + FP) * (TN + FN) )
    summary['MCC'] = ( ((TP * TN) - (FP * FN)) /
                       (1.0 if den == 0 else np.sqrt(den)) )

    if not positive_label is None:
        summary['sensitivity'] = summary[P]['true_rate']
        summary['specificity'] = summary[N]['true_rate']

        summary['precision'] = summary[P]['predictive_value']
        summary['recall'] = summary['sensitivity']

        summary['F_measure'] = (
                    2. * ((summary['precision'] * summary['recall']) /
                          (summary['precision'] + summary['recall']))
        )

    return summary


def _check_unique_labels(labels):
    labels = np.array([str(s).strip() for s in labels])
    unique_labels = np.unique(labels)

    if not len(unique_labels) == 2:
        raise L1L2SignatureException('more than 2 classes in labels.')

    unique_labels.sort(kind='mergesort')
    class1 = (labels == unique_labels[0])
    class2 = (labels == unique_labels[1])

    return unique_labels, class1, class2
