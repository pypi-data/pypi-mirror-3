#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import imp
import shutil
import cPickle as pkl

import numpy as np

import pplus
import l1l2py

from l1l2signature import internals as l1l2_core
from l1l2signature import utils as l1l2_utils

def main(config_path):
    # Configuration File
    config_dir = os.path.dirname(config_path)
    config = imp.load_source('config', config_path)

    # Data paths
    data_path = os.path.join(config_dir, config.data_matrix)
    labels_path = os.path.join(config_dir, config.labels)

    # Result dir initialization
    result_path = os.path.join(config_dir, config.result_path) #result base dir
    result_dir = l1l2_core.result_dir_init(result_path, config_path,
                                            data_path, labels_path)
    splits_dir = os.path.join(result_dir, 'splitsIO')

    print #--------------------------------------------------------------------
    print 'Reading data... '
    br = l1l2_utils.BioDataReader(data_path, labels_path,
                                  config.sample_remover,
                                  config.variable_remover,
                                  config.delimiter,
                                  config.samples_on,
                                  config.positive_label)
    data = br.data
    labels = br.labels

    print '  * Data shape:', data.shape
    print '  * Labels shape:', labels.shape

    print #--------------------------------------------------------------------
    print 'Generating parameters ranges...'
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

    print #-------------------------------------------------------------------
    print 'Setting parallel infrastructure...'
    pc = pplus.PPlusConnection(debug=config.debug)
    print '  * Experiment id: %s' % pc.id

    # Puts file on the disk
    pc.put('DATAFILE', data_path)
    pc.put('LABELFILE', labels_path)

    print #--------------------------------------------------------------------
    print 'Distributing external splits...',

    ext_k = config.external_k or len(labels)
    int_k = config.internal_k or (ext_k - 1)
    print '(# jobs = %d)' % ext_k

    ext_cv_sets = config.cv_splitting(labels, ext_k)
    sparse, regularized, return_predictions = (True, False, True)

    for i, (train_idxs, test_idxs) in enumerate(ext_cv_sets):
        input_key = 'in_split%d' % i #adds split ID to filename
        output_key = 'out_split%d' % i

        input_args=(config.sample_remover,
                    config.variable_remover,
                    config.delimiter,
                    config.samples_on,
                    config.positive_label,
                    train_idxs, test_idxs,
                    config.cv_splitting,
                    mu_range, tau_range, lambda_range,
                    int_k, config.cv_error, config.error,
                    config.data_normalizer, config.labels_normalizer,
                    sparse, regularized, return_predictions)

        # Saving args
        input_path = os.path.join(splits_dir, input_key)
        with open(input_path, 'w') as inputfile:
            pkl.dump(input_args, inputfile, pkl.HIGHEST_PROTOCOL)
        pc.put(input_key, input_path)

        print '  * Split %02d done!' % (i+1)
        pc.submit(modelselection_job,
                  args=(input_key, output_key),
                  depfuncs=(l1l2_utils.BioDataReader,
                            l1l2_utils.L1L2SignatureException,
                            l1l2_utils._check_unique_labels),
                  modules=('numpy as np', # needed by BioReader
                           'l1l2py', 'cPickle as pkl'))

    print #--------------------------------------------------------------------
    print 'Execution...'
    result_keys = pc.collect()

    if result_keys:
        print '  * Collected %d jobs on %d' % (len(result_keys), ext_k)
        print '  * Saving results data...',

        for output_key in result_keys:
            shutil.copy(pc.get_path(output_key), splits_dir)

        print 'done'
    else:
        print '  * Error, no results collected!'

    print #END ----------------------------------------------------------------

# PPlus Job function ----------------------------------------------------------
def modelselection_job(pc, input_key, output_key):

    # Importing inputs
    with open(pc.get_path(input_key)) as inputfile:
        tmp = pkl.load(inputfile)
    (sample_remover, variable_remover, delimiter, samples_on, positive_label,
     train_idxs, test_idxs, cv_splitting) = tmp[:8]
    args = tmp[8:]

    # Reading data
    br = BioDataReader(pc.get_path('DATAFILE'), pc.get_path('LABELFILE'),
                       sample_remover, variable_remover, delimiter, samples_on,
                       positive_label)
    data = br.data
    labels = br.labels

    # Calculating split submatrix
    Xtr, Ytr = data[train_idxs,:], labels[train_idxs,:]
    Xts,  Yts  = data[test_idxs, :], labels[test_idxs, :]

    # Parameters
    args = list(args) # writeble
    args[3] = cv_splitting(Ytr, args[3]) # args[3]=k -> splits

    # Execution
    result = l1l2py.model_selection(Xtr, Ytr, Xts, Yts, *args)

    # Saving outputs
    with pc.write_remotely(output_key) as resultfile:
        pkl.dump(result, resultfile, pkl.HIGHEST_PROTOCOL)

    return output_key

# Script entry ----------------------------------------------------------------
if __name__ == '__main__':
    from optparse import OptionParser
    from l1l2signature import __version__

    usage = "usage: %prog [-c] configuration-file.py"
    parser = OptionParser(usage=usage, version='%prog ' +  __version__)
    parser.add_option("-c", "--create", dest="create",
                      action="store_true",
                      help="create config file", default=False)
    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.error('incorrect number of arguments')
    config_file_path = args[0]

    if options.create:
        from l1l2signature import config
        std_config_path = config.__file__
        if std_config_path.endswith('.pyc'):
            std_config_path = std_config_path[:-1]

        if os.path.exists(config_file_path):
            parser.error('config file already exists')
        shutil.copy(std_config_path, config_file_path)
    else:
        main(os.path.abspath(config_file_path))
