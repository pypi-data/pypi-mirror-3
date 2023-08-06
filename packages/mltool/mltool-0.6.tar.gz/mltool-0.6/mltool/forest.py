"""
Random Forest training
----------------------

Implementation of a Random Forest training.

"""
import logging
from functools import partial
from multiprocessing import Pool
from collections import defaultdict

import numpy as np

from mltool.decisiontree import train_decision_tree, impurity_split
from mltool.utils import sample_dataset


log = logging.getLogger(__name__)


def rf_train_base((dataset, max_depth, ff, seed)):
    """Base function to create a tree for a random forest.

    """
    split_func = partial(impurity_split, ff=ff)
    try:
        return train_decision_tree(dataset, max_depth, split_func, seed)
    except:
        log.exception('Ops...')
        raise


def train_random_forest(dataset, num_trees, max_depth, ff, seed=1,
                        processors=None, callback=None):
    """Train a random forest model.

    :param dataset: the labelled dataset used for training
    :param num_trees: number of trees of the forest
    :param max_depth: maximum depth of the trees
    :param ff: feature fraction to use for the split (1.0 means all)
    :param seed: seed for the random number generator
    :param processors: number of processors to use (all if `None`)
    :param callback: function to call for each tree trained, it takes the new
                     tree as a parameter
    :type callback: `None` or callable

    :return: An mltool's model with with a forest of trees.

    """
    np.random.seed(seed)
    seeds = np.random.rand(num_trees)

    pool = Pool(processors)
    trees = pool.imap(rf_train_base, ((sample_dataset(dataset),
                                       max_depth, ff, seed) for seed in seeds))

    model = ['avg']
    total_gain = defaultdict(float)
    for tree, gain in trees:
        model.append(tree[2])

        for findex, score in gain.iteritems():
            total_gain[findex] += score

        if callback:
            callback(tree)

    return ('model', dataset.feature_names, tuple(model)), total_gain
