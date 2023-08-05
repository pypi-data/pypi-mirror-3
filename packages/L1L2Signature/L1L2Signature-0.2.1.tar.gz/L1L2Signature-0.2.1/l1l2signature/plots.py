"""Plot generation functions."""

# Author: Salvatore Masecchia <salvatore.masecchia@disi.unige.it>,
#         Annalisa Barla <annalisa.barla@disi.unige.it>
# License: new BSD.

import numpy as np
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.patches import Rectangle
from matplotlib.figure import figaspect
from matplotlib.colors import LinearSegmentedColormap

from .utils import _check_unique_labels


def kfold_errors(xrange, yrange, labels,
                 ts_errors, tr_errors=None, fig_num=None):
    """Returns a matplotlib figure object containing a kfold error plot.

    Parameters
    ----------
    xrange : iterable
        Range of values on the x-axis
    yrange : iterable
        Range of values on the y-axis
    labels : iterable
        Pair of string labels for X and Y axes
    ts_errors : :class:`numpy.ndarray`
        Test Error matrix (``float``) of dimensions
        ``len(xrange) X len(yrange)``
    tr_errors : :class:`numpy.ndarray`, optional
        Train Error matrix (``float``) of dimensions
        ``len(xrange) X len(yrange)``
    fig_num : int, optional
        Figure Number. If not given a new figure is initialized

    Returns
    -------
    fig : :class:`matplotlib.figure.Figure`
        Created figure handle

    """
    fig = plt.figure(fig_num)

    if len(xrange) == 1:
        _kcv_2d_plot(fig, xrange[0], yrange, labels, ts_errors, tr_errors)
    elif len(yrange) == 1:
        _kcv_2d_plot(fig, yrange[0], xrange, labels[::-1], ts_errors, tr_errors)
    else:
        _kcv_3d_plot(fig, xrange, yrange, labels, ts_errors, tr_errors)

    return fig


def _kcv_2d_plot(fig, xvalue, yrange, labels, ts_errors, tr_errors):
    # Fixed value as title
    plt.title('%s=%.3f' % (labels[0], xvalue))

    # Test Error curve
    plt.plot(yrange, ts_errors.T, 'bo-', label='Test Error')

    # Train Error curve
    if not tr_errors is None:
        plt.plot(yrange, tr_errors.T, 'ro-', label='Train Error')

    # Axis labes and legend
    plt.xlabel(labels[1])
    plt.ylabel('Error')
    plt.legend(loc='best')


def _kcv_3d_plot(fig, xrange, yrange, labels, ts_errors, tr_errors):
    # 3d initialization
    ax = fig.add_subplot(111, projection='3d')

    # Collection of legend handles
    legend_handles = []
    legend_labels = ['Test Error', 'Train Error']

    # Data
    x_vals, y_vals = np.meshgrid(xrange, yrange)
    x_idxs, y_idxs = np.meshgrid(np.arange(len(xrange)),
                                 np.arange(len(yrange)))

    # Test Error surface plot
    ax.plot_surface(x_vals, y_vals, ts_errors[x_idxs, y_idxs],
                    rstride=1, cstride=1, cmap=cm.Blues)
    legend_handles.append(Rectangle((0, 0), 1, 1, fc='b')) # proxy handle

    # Plot minimum Test error point
    x_min_idxs, y_min_idxs = np.where(ts_errors == ts_errors.min())
    ax.plot(xrange[x_min_idxs], yrange[y_min_idxs],
            ts_errors[x_min_idxs, y_min_idxs], 'bo')

    # Train Error surface plot
    if not tr_errors is None:
        ax.plot_surface(x_vals, y_vals, tr_errors[x_idxs, y_idxs],
                        rstride=1, cstride=1, cmap=cm.Reds)
        legend_handles.append(Rectangle((0, 0), 1, 1, fc='r')) # proxy handle

    # Axis labels and legend
    ax.set_xlabel(labels[0])
    ax.set_ylabel(labels[1])
    ax.set_zlabel('Error')

    ax.legend(legend_handles, legend_labels[:len(legend_handles)], loc='best')


def errors_boxplot(errors, positions, label=None, title=None, fig_num=None):
    """Returns a matplotlib figure object containing errors box plots.

    Parameters
    ----------
    errors : :class:`numpy.ndarray`
        Error matrix (``float``) of dimensions ``K X len(positions)``
    positions : :class:`numpy.ndarray`
        Box plot x axis
    label : str, optional
        X-Axis label
    title : str, optional
        Plot title
    fig_num : int, optional
        Figure Number. If not given a new figure is initialized

    Returns
    -------
    fig : :class:`matplotlib.figure.Figure`
        Created figure handle

    """
    fig = plt.figure(fig_num)

    errors = np.asarray(errors)
    plt.boxplot(errors, positions=positions)

    if title:
        plt.title(title)

    plt.ylabel('$error$')
    if label:
        plt.xlabel(label)

    # Symmetric plot around 0
    ymin, ymax = plt.ylim()
    plt.ylim(-ymax, ymax)

    return fig


def heatmap(submatrix, labels, sample_names=None, var_names=None,
            clustering_method='ward', clustering_metric='euclidean',
            fig_num=None):
    """Returns a matplotlib figure object containing an heatmap plot.

    If `scipy` is not installed samples and variables will be shown
    is given order.

    Parameters
    ----------
    submatrix : :class:`numpy.ndarray`
        Submatrix obtained from a signature.
    labels : :class:`numpy.ndarray`
        Samples labels.
    sample_names : iterable or str, optional
        Sample names. If None, heatmap will be anonymous.
    var_names : iterable or str, optional
        Variable names. If None, heatmap does not contain variables labels.
    clustering_method : str, optional (default 'ward')
        Clustering method used to order samples and variables.
        See :func:`scipy.cluster.hierarchy.linkage` function.
    clustering_metric : str, optional (default 'euclidean')
        Clustering metric used to order samples and variables.
        See :func:`scipy.cluster.hierarchy.linkage` function.
    fig_num : int, optional
        Figure Number. If not given a new figure is initialized

    Returns
    -------
    fig : :class:`matplotlib.figure.Figure`
        Created figure handle

    """
    try:
        from scipy.cluster.hierarchy import leaves_list, linkage
        scipy_found = True
    except ImportError:
        import warnings
        warnings.warn('Scipy not found, heatmap clustering parameters '
                      'will be ignored.')
        scipy_found = False

    # Splitting and checking labels
    unique_labels, class1, class2 = _check_unique_labels(labels)

    # Each gene is standardized across samples
    mean = submatrix.mean(axis=0)
    std = submatrix.std(axis=0, ddof=1)
    subX = (submatrix - mean)/std

    # Colormap: values close to 'gene column mean' are shown in black
    cdict = {
        'red':   ((0.0, 0.0, 0.0),
                  (0.5, 0.0, 0.1),
                  (1.0, 1.0, 1.0)),

        'green': ((0.0, 0.0, 1.0),
                  (0.5, 0.1, 0.0),
                  (1.0, 0.0, 0.0)),

        'blue':  ((0.0, 0.0, 0.0),
                  (1.0, 0.0, 0.0)),
    }
    green_red = LinearSegmentedColormap('GreenRed', cdict)

    n, m = subX.shape
    h, w = figaspect(m/float(n))
    fig = plt.figure(fig_num, figsize=(h, w))
    var_size = (6. * (h/m)) / 0.2   # Variables font size heuristic

    ax = fig.add_subplot(111)

    # Ordering by hierarchical clustering
    if scipy_found:
        # Samples are ordered class by class
        samples_order = np.r_[# First Class ordering
                              leaves_list(linkage(subX[class1],
                                                  clustering_method,
                                                  clustering_metric)),

                              # Second Class ordering (shifting indexes)
                              leaves_list(linkage(subX[class2],
                                                  clustering_method,
                                                  clustering_metric)) + sum(class1)
                              ]

        # Ordering also by variables
        heatmap = subX[samples_order].T
        var_order = leaves_list(linkage(heatmap,
                                        clustering_method,
                                        clustering_metric))

        # Final Ordering of heatmap and metadata
        heatmap = heatmap[var_order]
        if not var_names is None:
            var_names = var_names[var_order]
        if not sample_names is None:
            sample_names = sample_names[samples_order]

    else:
        heatmap = subX.T

    # Showing Heatmap
    im = ax.matshow(heatmap, aspect='auto', cmap=green_red)

    # y-labels (if not var_names: hidden)
    if not var_names is None:
        ax.set_yticks(np.arange(m))
        ax.set_yticklabels(var_names)
    else:
        ax.set_yticks([])

    for tick in ax.yaxis.get_major_ticks():
        tick.label1On = True
        tick.tick1On = False
        tick.label2On = False
        tick.tick2On = False
        tick.label.set_fontsize(var_size)

    # x-labels (if not sample_names: anonymous)
    ax.set_xticks(np.arange(n))
    if not sample_names is None:
        ax.set_xticklabels(sample_names)

    for tick in ax.xaxis.get_major_ticks():
        tick.label1On = True
        tick.tick1On = False
        tick.label2On = False
        tick.tick2On = False
        tick.label.set_rotation(90)
        tick.label.set_fontsize(6)

    ax.set_title('%s vs %s' % tuple(unique_labels))
    ax.axvline(sum(class1) - 0.5, color='y', lw=3)

    #from mpl_toolkits.axes_grid import make_axes_locatable
    #divider = make_axes_locatable(ax)
    #cax = divider.append_axes('top', size=0.3, pad=0.5)
    #ticks = [subX.min(), (subX.max() + subX.min()) / 2., subX.max()]
    #cbar = plt.colorbar(im, cax=cax, orientation='orizontal', ticks=ticks)
    #cbar.ax.set_xticklabels(['Low', 'Medium', 'High'], fontsize=6)

    return fig


def pca(submatrix, labels, fig_num=None):
    """Returns a matplotlib figure containing sample points.

    Starting from given ``submatrix`` calculates a PCA projection to plot
    samples in a 3D-space. If the signatures contains only 2 or 3 variables,
    PCA is obviously not performed.

    Parameters
    ----------
    submatrix : :class:`numpy.ndarray`
        Submatrix obtained from a signature.
    labels : :class:`numpy.ndarray`
        Samples labels.
    fig_num : int, optional
        Figure Number. If not given a new figure is initialized

    Returns
    -------
    fig : :class:`matplotlib.figure.Figure`
        Created figure handle

    """
    # Data centering
    X = submatrix - submatrix.mean(axis=0)

    fig = plt.figure(fig_num)

    # Collection of legend handles
    legend_handles = []

    # Splitting and checking labels
    unique_labels, class1, class2 = _check_unique_labels(labels)

    n, d = X.shape

    if d > 2:
        if n >= d:
            U, S, VT = np.linalg.svd(X, full_matrices=False)
            Xproj = np.dot(X, VT[:3, :].T)
        else:
            U, S, VT = np.linalg.svd(X.T, full_matrices=False)
            Xproj = np.dot(X, U[:, :3])

        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(Xproj[class1, 0],
                   Xproj[class1, 1],
                   Xproj[class1, 2], c='b', marker='o')
        ax.scatter(Xproj[class2, 0],
                   Xproj[class2, 1],
                   Xproj[class2, 2], c='r', marker='o')

        # proxy handles
        legend_handles.append(Rectangle((0, 0), 1, 1, fc='b'))
        legend_handles.append(Rectangle((0, 0), 1, 1, fc='r'))

        ax.set_xlabel('PC 1')
        ax.set_ylabel('PC 2')
        ax.set_zlabel('PC 3')

        # Axis legend
        ax.legend(legend_handles, unique_labels, loc='best')

    elif d == 2:
        ax = fig.add_subplot(111)
        ax.scatter(X[class1,0],
                   X[class1,1], c='b', marker='o', label=unique_labels[0])
        ax.scatter(X[class2,0],
                   X[class2,1], c='r', marker='o', label=unique_labels[1])

        ax.set_xlabel(var_names[0])
        ax.set_ylabel(var_names[1])
        ax.legend(loc='best')
    else:
        ax = fig.add_subplot(111)
        ax.scatter(X[class1],
                   np.zeros_like(X[class1]), c='b', marker='o',
                   label=unique_labels[0])
        ax.scatter(X[class2],
                   np.zeros_like(X[class2]), c='r', marker='o',
                   label=unique_labels[1])

        ax.set_xlabel(var_names[0])
        ax.legend(loc='best')

    return fig


def selected_over_threshold(frequencies, mu_range, fig_num=None):
    """Returns a figure containing a plot of selected vars cumulative counting.

    For each mu value plots a curve which indicates how many variables
    are been selected for each frequency threshold.

    Parameters
    ----------
    frequencies : :class:`numpy.ndarray`
        List of ``len(mu_range)`` lists containing coordinates to plot.
    mu_range : class:`numpy.ndarray`
        Range of mu values.
    fig_num : int, optional
        Figure Number. If not given a new figure is initialized

    Returns
    -------
    fig : :class:`matplotlib.figure.Figure`
        Created figure handle

    """
    fig = plt.figure(fig_num)

    for i, (mu, (x, y)) in enumerate(zip(mu_range, frequencies)):
        plt.plot(x, y, 'o-', label='$\mu_%d = %.3f$' % (i+1, mu), lw=2)

    # Axis limits
    for lim_func in (plt.xlim, plt.ylim):
        amin, amax = lim_func()
        offset = 0.1 * (amax - amin)
        lim_func(amin-offset, amax+offset)

    plt.xlabel('frequency threshold')
    plt.ylabel('number of variables')

    plt.grid()
    plt.legend(loc='best')

    return fig
