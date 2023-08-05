"""Internal utilities functions."""

# Author: Salvatore Masecchia <salvatore.masecchia@disi.unige.it>,
#         Annalisa Barla <annalisa.barla@disi.unige.it>
# License: new BSD.

import os
import shutil
import datetime
import cPickle as pickle

import numpy as np


def result_dir_init(result_path, config_path, data_path, labels_path):
    """Creates a new result directory.

    The function creates a new result directory in ``result_path``.
    The result directory is initialized copying the configuration file
    (named as ``config.py``) and creating two (Unix) hard links for data
    and labels files.

    The obtained result dir is now self-contained. This simplify collection
    and backup of result directories.

    Parameters
    ----------
    result_path : str
        Result base absolute path (parent directory).
    config_path : str
        Configuration file absolute path
    data_path : str
        Data matrix absolute path.
    labels_path : str
        Labels absolute path.

    Returns
    -------
    result_dir : str
        Experiment result directory path

    """
    # Paths normalization
    config_path = os.path.normpath(config_path)
    result_path = os.path.normpath(result_path)
    data_path = os.path.normpath(data_path)
    labels_path = os.path.normpath(labels_path)

    # Directory creation
    date = datetime.datetime.now().isoformat()
    basedir = os.path.dirname(config_path)
    result_dir = os.path.normpath(os.path.join(basedir,
                                               result_path,
                                               'l1l2_result_%s' % date))
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)
        os.makedirs(os.path.join(result_dir, 'splitsIO'))

    # Copy config file
    shutil.copy(config_path, os.path.join(result_dir, 'config.py'))

    # Hard link for data into the result dir
    data_file_name = os.path.split(data_path)[-1]
    os.link(data_path, os.path.join(result_dir, data_file_name))

    # Hard link for labels into the result dir
    labels_file_name = os.path.split(labels_path)[-1]
    os.link(labels_path, os.path.join(result_dir, labels_file_name))

    return result_dir


def read_pkls(result_dir, kind):
    """Reads all the pickled input/output of an experiment.

    Outputs will be returned sorted by split number.

    Parameters
    ----------
    result_dir : str
        Experiment result dir path

    kind : str
        Kind of pickles to read: 'input' or 'output'

    Returns
    -------
    pkls : list
        List of experiment input/outputs

    """
    mapping = {'input': 'in_split', 'output': 'out_split'}

    try:
        what = mapping[kind]
    except KeyError:
        raise Exception("Invalid 'kind' value: %s" % kind)

    splits_dir = os.path.join(result_dir, 'splitsIO')
    pkls_paths = [os.path.join(splits_dir, f) for f in os.listdir(splits_dir)
                                              if f.startswith(what)]
    pkls = list()
    for pkl_path in pkls_paths:
        split_num = pkl_path.split(what)[-1] # extract split number
        with open(pkl_path) as pkl:
            pkls.append((int(split_num), pickle.load(pkl)))

    # Sort by split number and then extract only results
    return zip(*sorted(pkls))[1]


## Textual results ------------------------------------------------------------
class StatsWriter(object):
    """Stats result generator.

    Given a file object, is possible to write some tables summarizing
    results of an experiment.

    Parameters
    ----------
    fileobj : file
        File object open in write mode. User is responsible to
        open and close the given file

    """
    def __init__(self, fileobj):
        self._sfile = fileobj

        self._writeline('*L1L2 Signature* experiment summary')
        self._writeline('===================================')

    def _newline(self, n=1):
        self._sfile.write('\n' * n)

    def _writeline(self, content, nl_before=0, nl_after=1):
        self._newline(nl_before)
        self._sfile.write(content)
        self._newline(nl_after)

    def write_optimal_parameters(self, splits_results, title):
        """Writes optimal parameters table.

        The table contain all pairs of optimal parameters found in each
        experiment external splits.

        Parameters
        ----------
        splits_results : iterable
            List of results from L1L2Py module, one for each external split.
        title : str
            Table title (it will be printed above the table).

        """
        # Title
        self._writeline(title, 2)
        self._writeline('=' * 74)

        # Header
        header_fmt = '{:<10}|{:^15}|{:^15}|{:^15}|{:^15}'
        header = header_fmt.format('Split  #', 'lambda*', 'tau*',
                                   'log(lam*)', 'log(tau*)')
        self._writeline(header)
        self._writeline('+'.join(['-'*10, '-'*15, '-'*15, '-'*15, '-'*15]))

        # Data
        data_fmt = 'Split {:3d} | {:13.3f} | {:13.3f} | {:13.3f} | {:13.3f} '
        for i, split_out in enumerate(splits_results):
            line = data_fmt.format((i+1),
                                   split_out['lambda_opt'],
                                   split_out['tau_opt'],
                                   np.log10(split_out['lambda_opt']),
                                   np.log10(split_out['tau_opt']))

            self._writeline(line)


    def write_prediction_errors(self, errors, title):
        """Writes prediction errors table.

        The table contains a summary of the estimated prediction errors
        (averaged over external splits results) for each correlation value (mu).

        Parameters
        ----------
        errors : :class:`numpy.ndarray` (-like)
            Data matrix (``float``) of dimensions ``splits X len(mu_range)``
        title : str
            Table title (it will be printed above the table).

        """
        # Data checking
        errors = np.asanyarray(errors, dtype=float)

        # Title
        self._writeline(title, 2)
        self._writeline('=' * (10 + 16 * errors.shape[1]))

        # Header
        header_fmt = ''.join(('{:<10}',
                              '|{:^15}' * errors.shape[1]))
        mu_list = ('mu%d' % i for i in xrange(1, errors.shape[1]+1))
        header = header_fmt.format('Stat type', *mu_list)
        self._writeline(header)
        self._writeline('+'.join(['-'*10] + ['-'*15] * errors.shape[1]))

        # Data formatter
        data_fmt = ''.join(('{:<10}',
                            '| {:13.3f} ' * errors.shape[1]))

        # Errors Mean
        self._writeline(data_fmt.format('mean',
                                        *errors.mean(axis=0)))
        self._writeline(data_fmt.format('std',
                                        *errors.std(axis=0, ddof=1)))
        self._writeline(data_fmt.format('median',
                                        *np.median(errors, axis=0)))

        # Separator
        self._writeline('+'.join(['-'*10] + ['-'*15] * errors.shape[1]))

        # Sqrt Errors
        self._writeline(data_fmt.format('sqrt(mean)',
                                        *np.sqrt(errors.mean(axis=0))))
        self._writeline(data_fmt.format('sqrt(std)',
                                        *np.sqrt(errors.std(axis=0, ddof=1))))
        self._writeline(data_fmt.format('sqrt(med)',
                                        *np.sqrt(np.median(errors, axis=0))))

    def write_classification_summary(self, cm, measures,
                                     positive_label, title):
        """Writes confusion matrix table and classification measures.

        Parameters
        ----------
        cm : dict
            Dictionary containing a confusion matrix.
        measures : dict
            Dictionary containing classification measures.
        positive_label : str
            Indicates if a positive label has to be considered.
        title : str
            Table title (it will be printed above the table).

        """
        self._writeline(title, 2)

        # Data formatter
        data_fmt = '{:>15} |{:^20}|{:^20}|{:>20}'

        labels = cm['T'].keys()
        if not positive_label is None:
            P = positive_label
            N = set(labels).difference([positive_label]).pop()
        else:
            P, N = sorted(labels)

        header = data_fmt.format('Real vs Pred.', P, N, 'Predictive Values')
        separator = '+'.join(('-'*16, '-'*20, '-'*20, '-'*20))
        self._writeline('=' * len(header))
        self._writeline(header)

        self._writeline(separator)
        PPV = measures[P]['predictive_value'] * 100
        self._writeline(data_fmt.format(P, '%3d' % cm['T'][P], '%3d' % cm['F'][P],
                                        '%3.2f %%' % PPV))

        self._writeline(separator)
        NPV = measures[N]['predictive_value'] * 100
        self._writeline(data_fmt.format(N, '%3d' % cm['F'][N], '%3d' % cm['T'][N],
                                        '%3.2f %%' % NPV))

        self._writeline(separator)
        self._writeline(data_fmt.format('True rates',
                                        '%3.2f %%' % (measures[P]['true_rate'] * 100),
                                        '%3.2f %%' % (measures[N]['true_rate'] * 100),
                                        ''))

        self._writeline('Classification performance measures:', 2)
        self._writeline('  * Accuracy:          %3.2f %%' % (measures['accuracy'] * 100))
        self._writeline('  * Balanced Accuracy: %3.2f %%' % (measures['balanced_accuracy'] * 100))
        self._writeline('  * MCC:               %3.2f %%' % (measures['MCC'] * 100))

        if not positive_label is None:
            self._writeline('Considering %s as the '
                            'positive class:' % positive_label, 2)
            self._writeline('  * Sensitivity:   %3.2f %%' % (measures['sensitivity'] * 100))
            self._writeline('  * Specificity:   %3.2f %%' % (measures['specificity'] * 100))
            self._writeline('  * Precision:     %3.2f %%' % (measures['precision'] * 100))
            self._writeline('  * Recall:        %3.2f %%' % (measures['recall'] * 100))
            self._writeline('  * F-measure:     %3.2f %%' % (measures['F_measure'] * 100))
