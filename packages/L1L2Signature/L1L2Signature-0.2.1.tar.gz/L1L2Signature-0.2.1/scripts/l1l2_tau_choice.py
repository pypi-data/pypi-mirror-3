#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import imp

import numpy as np
from matplotlib import pyplot as plt

import l1l2py

from l1l2signature import utils as l1l2_utils

def main(config_path, show=False):
    config_dir = os.path.dirname(config_path)
    config = imp.load_source('config', config_path)

    # Data paths
    data_path = os.path.join(config_dir, config.data_matrix)
    labels_path = os.path.join(config_dir, config.labels)

    print #--------------------------------------------------------------------
    print 'Reading data... '
    br = l1l2_utils.BioDataReader(data_path, labels_path,
                                  config.sample_remover,
                                  config.variable_remover,
                                  config.delimiter,
                                  config.samples_on)

    data = br.data
    labels = br.labels

    print '  * Data shape:', data.shape
    print '  * Labels shape:', labels.shape

    print #-------------------------------------------------------------------
    print 'Extreme parameters (max. tau and min. mu) calculation...'
    rs = l1l2_utils.RangesScaler(data, labels, config.data_normalizer,
                                 config.labels_normalizer)

    max_tau = rs.tau_scaling_factor
    mu_value = rs.mu_scaling_factor * 1e-3
    print '  * Max tau:  %.3e' % max_tau
    print '  * Mu value: %.3e (mu_scale * 1e-3)' % mu_value

    beta, k = l1l2py.algorithms.l1l2_regularization(rs.norm_data,
                                                    rs.norm_labels,
                                                    mu_value,
                                                    max_tau,
                                                    return_iterations=True)
    selected = beta.ravel().nonzero()
    print '  * Selected %d valiable(s) in %d iterations' % (len(*selected), k)

    print #--------------------------------------------------------------------
    print 'L1L2 path... (from bigger to smaller tau)'
    tau_range = np.sort(config.tau_range) * max_tau

    print '  * From tau: %.3e (not scaled: %.3e)' % (tau_range[-1],
                                                     config.tau_range[-1])
    print '  * To tau:   %.3e (not scaled: %.3e)' % (tau_range[0],
                                                     config.tau_range[0])
    print ''.join(['  ', '-'*42])
    print '  tau\t\t#variables\t#iterations'
    print ''.join(['  ', '-'*42])

    beta_prev = np.zeros(data.shape[1])
    for t in tau_range[::-1]:
        beta, k = l1l2py.algorithms.l1l2_regularization(rs.norm_data,
                                                        rs.norm_labels,
                                                        mu_value, t,
                                                        beta=beta_prev,
                                                        return_iterations=True)
        print '  %.3e\t%d\t\t%d' % (t, len(*beta.ravel().nonzero()), k)
        beta_prev = beta

    print ''.join(['  ', '-'*42])

    print #--------------------------------------------------------------------
    print 'L1 5-fold error estimation... (press CTRL-C to stop)'

    K = 5 # config.external_k or len(Y)
    cv_error = list()
    tr_cv_error = list()

    try:
        for i, (tr, ts) in enumerate(config.cv_splitting(labels, K)):

            Xtr, Ytr = data[tr], labels[tr]
            Xts, Yts = data[ts], labels[ts]

            if config.data_normalizer:
                Xtr, Xts = config.data_normalizer(Xtr, Xts)

            if config.labels_normalizer:
                Ytr, Yts = config.labels_normalizer(Ytr, Yts)

            print '  * Split %d/%d...' % ((i+1), K),
            sys.stdout.flush()

            beta_path = l1l2py.algorithms.l1l2_path(Xtr, Ytr, mu_value, tau_range)
            split_errors = list()
            tr_split_errors = list()

            for beta in beta_path:
                selected = beta.ravel().nonzero()[0]

                Xtr_sel = Xtr[:, selected]
                Xts_sel = Xts[:, selected]
                bsel = beta.ravel()[selected]

                split_errors.append(config.cv_error(Yts, np.dot(Xts_sel, bsel)))
                tr_split_errors.append(config.cv_error(Ytr, np.dot(Xtr_sel, bsel)))

            cv_error.append(split_errors)
            tr_cv_error.append(tr_split_errors)
            print 'done.'

    except KeyboardInterrupt:
        print 'interrupted!'

    # To avoid different length
    min_len = min(len(cv_error), len(tr_cv_error))
    cv_error = cv_error[:min_len]
    tr_cv_error = tr_cv_error[:min_len]

    if cv_error: # Not empty
        cv_error = np.asarray(cv_error).mean(axis=0)
        tr_cv_error = np.asarray(tr_cv_error).mean(axis=0)

        print '  * Generating mean kcv-error plot...'
        plt.figure()
        plt.title('Mean kcv-error (%d on %d splits)' % (min_len, K))
        plt.xlabel('log(tau)')
        plt.ylabel('error')
        plt.semilogx(tau_range, tr_cv_error, 'r.-', label='train error')
        plt.semilogx(tau_range, cv_error, 'b.-', label='test error')
        plt.legend(loc='best')

        plot_path = os.path.join(config_dir, 'tau_choice_plot.png')
        print '  * Saving generated plot (%s)...' % plot_path
        plt.savefig(plot_path)

        if show:
            plt.show()

    print # End ---------------------------------------------------------------

# Script entry ----------------------------------------------------------------
if __name__ == '__main__':
    from optparse import OptionParser
    from l1l2signature import __version__

    usage = "usage: %prog [-s] configuration-file.py"
    parser = OptionParser(usage=usage, version='%prog ' +  __version__)
    parser.add_option("-s", "--show", dest="show",
                      action="store_true",
                      help="show interactive plot", default=False)
    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.error('incorrect number of arguments')
    config_file_path = args[0]

    main(os.path.abspath(config_file_path), options.show)
