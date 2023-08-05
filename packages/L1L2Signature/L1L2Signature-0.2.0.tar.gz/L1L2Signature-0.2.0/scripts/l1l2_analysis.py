#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import imp
import csv
import itertools as it

import numpy as np

import matplotlib

def main(result_dir, show):

    # Local imports, in order to select backend on startup
    from matplotlib import pyplot as plt
    from l1l2signature import internals as l1l2_core
    from l1l2signature import utils as l1l2_utils
    from l1l2signature import plots as l1l2_plot

    config = imp.load_source('config', os.path.join(result_dir, 'config.py'))

    print #--------------------------------------------------------------------
    print 'Reading data... '

    data_file_name = os.path.split(config.data_matrix)[-1]
    data_path = os.path.join(result_dir, data_file_name)

    labels_file_name = os.path.split(config.labels)[-1]
    labels_path = os.path.join(result_dir, labels_file_name)

    br = l1l2_utils.BioDataReader(data_path, labels_path,
                                  config.sample_remover,
                                  config.variable_remover,
                                  config.delimiter,
                                  config.samples_on)
    data = br.data
    labels = br.labels
    sample_names = br.samples
    probeset_names = br.variables

    print '  * Data shape:', data.shape
    print '  * Labels shape:', labels.shape

    # Creating Stats writer ---------------------------------------------------
    stats_table = open(os.path.join(result_dir, 'stats.txt'), 'w')
    sw = l1l2_core.StatsWriter(stats_table)

    print #--------------------------------------------------------------------
    print 'Reading pickled outputs...'
    outputs = l1l2_core.read_pkls(result_dir, 'output')
    print '  * Read %d partial results' % len(outputs)
    sw.write_optimal_parameters(outputs, 'Optimal Parameters')

    print #--------------------------------------------------------------------
    print 'Generating parameters ranges (from configuration file)...'
    rs = l1l2_utils.RangesScaler(data, labels, config.data_normalizer,
                                               config.labels_normalizer)

    tau_range = rs.tau_range(np.sort(config.tau_range))
    mu_range = rs.mu_range(np.sort(config.mu_range))
    lambda_range = np.sort(config.lambda_range)

    for name, range in (('tau', tau_range), ('mu', mu_range),
                        ('lambda', lambda_range)):
        print '  * %2d values of %6s from %8.3f to %8.3f' % (len(range), name,
                                                             range[0],
                                                             range[-1])

    print #--------------------------------------------------------------------
    print 'Generating and saving KCV errors plots...'

    # Maximum number of valid tau values across all splits
    valid_tau_num = len(tau_range)

    kfold_err_ts = list()
    kfold_err_tr = list()
    err_ts = list()
    err_tr = list()

    # Outputs assumed ordered by split number (even if pplus reschedules jobs)
    for i, out in enumerate(outputs):
        split_valid_tau_num = out['kcv_err_ts'].shape[0]
        valid_tau_num = np.min((split_valid_tau_num, valid_tau_num))

        # Plotting error surfaces
        l1l2_plot.kfold_errors(np.log10(tau_range[:split_valid_tau_num]),
                                  np.log10(lambda_range),
                                  ('$log_{10}(\\tau)$','$log_{10}(\lambda)$'),
                                  out['kcv_err_ts'],
                                  out['kcv_err_tr'],
                                  fig_num=i)

        plt.suptitle('EXT. SPLIT %d KCV ERROR vs. TAU, LAMBDA' % (i+1))
        plt.savefig(os.path.join(result_dir, 'kcv_err_split_%d.png' % (i+1)))

        # Saving kcv and prediction errors
        kfold_err_ts.append(out['kcv_err_ts'])
        kfold_err_tr.append(out['kcv_err_tr'])
        err_ts.append(out['err_ts_list'])
        err_tr.append(out['err_tr_list'])

    # Extracting common columns in order to average errors
    avg_kfold_err_ts = np.empty((len(kfold_err_ts), valid_tau_num, len(lambda_range)))
    avg_kfold_err_tr = np.empty((len(kfold_err_tr), valid_tau_num, len(lambda_range)))
    for i, (tmp_ts, tmp_tr) in enumerate(zip(kfold_err_ts, kfold_err_tr)):
        avg_kfold_err_ts[i] = tmp_ts[:valid_tau_num,:]
        avg_kfold_err_tr[i] = tmp_tr[:valid_tau_num,:]

    # Averaging and plotting errors
    avg_kfold_err_ts = avg_kfold_err_ts.mean(axis=0)
    avg_kfold_err_tr = avg_kfold_err_tr.mean(axis=0)
    l1l2_plot.kfold_errors(np.log10(tau_range[:valid_tau_num]),
                              np.log10(lambda_range),
                              ('$log_{10}(\\tau)$','$log_{10}(\lambda)$'),
                              avg_kfold_err_ts,
                              avg_kfold_err_tr)
    plt.suptitle('AVG KCV ERROR vs. TAU, LAMBDA')
    plt.savefig(os.path.join(result_dir, 'avg_kcv_err.png'))

    print #--------------------------------------------------------------------
    print 'Generating and saving prediction errors plots...'

    fig = l1l2_plot.errors_boxplot(err_ts, np.log10(mu_range),
                                   '$log_{10}(\\mu)$', 'TEST ERROR vs. MU')
    plt.savefig(os.path.join(result_dir, 'prediction_error_ts.png'))

    fig = l1l2_plot.errors_boxplot(err_tr, np.log10(mu_range),
                                   '$log_{10}(\\mu)$', 'TRAINING ERROR vs. MU')
    plt.savefig(os.path.join(result_dir, 'prediction_error_tr.png'))

    sw.write_prediction_errors(err_ts, 'Test set Prediction')
    sw.write_prediction_errors(err_tr, 'Training set Prediction')

    print #--------------------------------------------------------------------
    print 'Generating signatures...'

    (sign_totals,
     sign_freqs,
     sign_idxs) = l1l2_utils.signatures(outputs, config.frequency_threshold)

    # A signature for each correlation value
    for i in xrange(len(mu_range)):

        table_path = os.path.join(result_dir, 'signature_mu%d.txt' % (i+1))
        with open(table_path, 'wb') as freqs_table:
            writer = csv.DictWriter(freqs_table,
                                    ('index', 'probe', 'freq', 'num_sel'),
                                    dialect=csv.excel_tab)
            writer.writeheader()

            # Rows
            rows = ({'index': str(idx),
                     'probe': probeset_names[idx],
                     'freq': '%.3f' % freq,
                     'num_sel': '%d/%d' % (int(tot), len(outputs))}
                        for idx, tot, freq in zip(sign_idxs[i],
                                                  sign_totals[i],
                                                  sign_freqs[i])
                   )
            writer.writerows(rows)

    print #--------------------------------------------------------------------
    print 'Generating and saving selected variables counting...'
    sign_freqs = l1l2_utils.signatures(outputs)[1] # Freqs without cut

    # X axis
    x_freqs = (np.arange(len(outputs)+1) / float(len(outputs)))

    # Table parameters
    data_fmt = ''.join(('  {:^15.3e} ',
                        '| {:7} ' * len(x_freqs)))
    hdr_fmt = '| {:6.2f}% ' * len(x_freqs)
    row_len = 10 * len(x_freqs) # len(" XXXXXX% |")

    # Table header
    print '  -----------------%s' % ('-' * (row_len))
    print '                  |%s' % '# selected variables'.center(row_len)
    print '        mu        +%s' % ('-' * row_len)
    print '                  %s' % hdr_fmt.format(*(x_freqs*100))
    print '  -----------------%s' % ('-' * (row_len))

    # Plot coords calculation and print
    frequencies = list()
    for i, (mu, freqs) in enumerate(zip(mu_range, sign_freqs)):

        # Default result
        selected = dict(zip(x_freqs, [0]*len(x_freqs)))

        # Calculation
        for b, g in it.groupby(freqs):
            selected[b] = len(list(g))

        # Sorted by cut
        cut, selected = zip(*sorted(selected.items()))
        selected = np.cumsum(selected[::-1])[::-1]
        frequencies.append((cut[1:], selected[1:])) # without 0%

        # Table row
        print data_fmt.format(mu, *selected)

    # Plot
    l1l2_plot.selected_over_threshold(frequencies, mu_range)
    plt.savefig(os.path.join(result_dir, 'selected_over_threshold.png'))

    # -------------------------------------------------------------------------
    if len(np.unique(labels)) == 2: # Classification

        print # ---------------------------------------------------------------
        print 'Confusion matrix calculation...'
        print '  * Reading pickled inputs...',
        inputs = l1l2_core.read_pkls(result_dir, 'input')
        print 'read %d splits inputs' % len(inputs)

        print '  * Calculating predicted labels over splits...'
        pred_labels = np.zeros((len(mu_range), len(labels))) # for each mu
        for inp, out in zip(inputs, outputs):
            ts_idxs = inp[6] # External split indexes
            pred = np.sign(out['prediction_ts_list'])
            pred_labels[:,ts_idxs] = pred.squeeze()

        print '  * Saving classification performances measures...'
        real_labels = [br.labels_reverse[c] for c in br.labels] # True Labels
        measures_list = list()
        for i in xrange(len(mu_range)):
            mapped_prediction = [br.labels_reverse[c] for c in pred_labels[i]]
            cm = l1l2_utils.confusion_matrix(real_labels, mapped_prediction)
            measures = l1l2_utils.classification_measures(cm,
                                                          config.positive_label)

            sw.write_classification_summary(cm, measures, config.positive_label,
                                    'Confusion matrix and classification '
                                    'performance with mu%d' % (i+1))

        print # ---------------------------------------------------------------
        print ('Extracting (by signatures) and ordering '
               '(by frequencies) submatrices...')
        # Sub matrices are also ordered by frequencies
        labels_idxs, sub_matrices = l1l2_utils.ordered_submatrices(data,
                                                                   labels,
                                                                   sign_idxs)
        # Labels and sample names sorted according to submatrices
        lab_sorted = labels[labels_idxs]
        sample_names_sorted = sample_names[labels_idxs]

        # Real labels names
        real_labels = np.array([br.labels_reverse[c] for c in lab_sorted])

        print # ---------------------------------------------------------------
        print 'Generating and saving heatmaps...'

        for i, (subm, sign) in enumerate(zip(sub_matrices, sign_idxs)):
            l1l2_plot.heatmap(subm, real_labels, sample_names_sorted,
                              probeset_names[sign])
            plt.savefig(os.path.join(result_dir, 'heatmap_mu%d.png' % (i+1)),
                        bbox_inches='tight')

        print #----------------------------------------------------------------
        print 'PCA plotting....'

        for i, subm in enumerate(sub_matrices):
            l1l2_plot.pca(subm, real_labels)
            plt.suptitle('PCA PROJECTION (signature with mu%d)' % (i+1))
            plt.savefig(os.path.join(result_dir, 'pca_mu%d.png' % (i+1)))

    stats_table.close() # No more stats
    print # empty line

    if show:
        plt.show()

# Script entry ----------------------------------------------------------------
if __name__ == '__main__':
    from optparse import OptionParser
    from l1l2signature import __version__

    usage = "usage: %prog result-dir"
    parser = OptionParser(usage=usage, version='%prog ' +  __version__)
    parser.add_option("-d", "--dpi", dest="dpi",
                      action="store",
                      help="figures dpi resolution (default 300)",
                      default=300)
    parser.add_option("-s", "--show", dest="show",
                      action="store_true",
                      help="show interactive plots", default=False)
    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.error('incorrect number of arguments')

    if not options.show:
        matplotlib.use('Agg') # no show

    matplotlib.rcParams['savefig.dpi'] = options.dpi
    result_dir = args[0]

    main(os.path.abspath(result_dir), options.show)
