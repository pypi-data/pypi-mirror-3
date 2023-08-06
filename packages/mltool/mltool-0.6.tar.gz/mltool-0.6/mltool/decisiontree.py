#!/usr/bin/env python
"""
Decision Tree
-------------

Very simple decision tree implementation.

"""
import numpy as np
import random
from collections import defaultdict


def all_same(v):
    return (v == v[0]).all()


def indent(s):
    return '\n'.join('| ' + v for v in s.splitlines())


def impurity_split(labels, samples, ff=1.0):
    I_best = None

    lin_total = np.sum(labels)
    sq_total = np.sum(labels * labels)

    L_len = np.arange(1, len(labels))
    R_len = np.arange(len(labels)-1, 0, -1)

    f_selected = max(1, int(round(len(samples) * ff)))
    f_indices = np.array(random.sample(xrange(len(samples)), f_selected))

    for f_index in f_indices:
        f_vec = samples[f_index]
        order = np.argsort(f_vec)

        lin = np.take(labels, order[:-1])
        sq = lin * lin

        L_lin = np.cumsum(lin)
        L_sq = np.cumsum(sq)

        R_lin = lin_total - L_lin
        R_sq = sq_total - L_sq

        L_mean = L_lin / L_len
        R_mean = R_lin / R_len

        L = L_sq - (L_mean * L_mean) * L_len
        R = R_sq - (R_mean * R_mean) * R_len
        assert len(R) == len(L) == (len(order) - 1)
        assert (R >= 0).all()
        assert (L >= 0).all()

        I = L + R
        diff = np.diff(np.take(f_vec, order))
        if not diff.any():
            continue

        remove_same = (diff == 0) * (np.max(I) + 1)

        local_min = np.argmin(I + remove_same)

        if I_best is None or I[local_min] < I_best:
            I_best = I[local_min]
            split_index = f_index
            split_value = (f_vec[order[local_min]]
                           + f_vec[order[local_min+1]]) / 2

            # floating point errors can invalidate the following assertion
            #   split_value < f_vec[order[local_min+1]]
            # in this case is just better to take f_vec[order[local_min]]
            if split_value >= f_vec[order[local_min+1]]:
                split_value = f_vec[order[local_min]]

    if I_best is None:
        return None
    else:
        err = sq_total - lin_total/len(labels)
        assert err >= I_best
        return split_index, split_value, err - I_best


class DTNode(object):
    """Decision/Regression Tree node"""

    def __init__(self, labels, samples, max_depth,
                 split_func=impurity_split):
        assert max_depth >= 0

        self._leaf = True
        self._value = np.average(labels)

        if max_depth == 0 or len(labels) <= 1 or all_same(labels):
            return

        split_result = split_func(labels, samples)
        if split_result is None:
            return

        self._leaf = False
        f_index, f_value, f_gain = split_result

        left_indices = samples[f_index, :] <= f_value
        left_labels = np.compress(left_indices, labels)
        left_samples = np.compress(left_indices, samples, axis=1)

        right_indices = np.invert(left_indices)
        right_labels = np.compress(right_indices, labels)
        right_samples = np.compress(right_indices, samples, axis=1)

        assert len(left_labels) + len(right_labels) == len(labels)
        assert len(left_labels) > 0 and len(right_labels) > 0

        self._split_feature = f_index
        self._split_value = f_value
        if f_gain != 0:
            self._gain = f_gain
        else:
            self._gain = 0.0
        self._left_child = DTNode(left_labels, left_samples,
                                  max_depth-1, split_func)
        self._right_child = DTNode(right_labels, right_samples,
                                   max_depth-1, split_func)

    def predict(self, sample):
        if self._leaf:
            return self._value

        if sample[self._split_feature] <= self._split_value:
            return self._left_child.classify(sample)
        else:
            return self._right_child.classify(sample)

    def __str__(self):
        if self._leaf:
            return '- = %s' % self._value
        else:
            return '- %s <= %s\n%s\n%s' % (self._split_feature,
                                           self._split_value,
                                           indent(str(self._left_child)),
                                           indent(str(self._right_child)))


def train_decision_tree(dataset, max_depth,
                        split_func=None, seed=None):
    """Train a decision tree for regression.

    It is possible to customize the function used to find the split for each
    node in the tree. The ``split_func`` is a callable that accepts two
    parameters, an array of labels and an 2d-array of samples. It returns None
    if no split is found, otherwise a tuple with the index of the feature,
    the value for the split and a gain score.

    The 2d-array of samples has one column for each sample and one row per
    feature.

    :param dataset: the labelled dataset used for training
    :param max_depth: maximum depth of the trees
    :param split_func: function to use to find the split.
                       If `None` then a default one is used.
    :param seed: seed for the random number generator
    :type split_func: `None` or callable

    :return: An mltool's model with a single decision tree.

    """
    if split_func is None:
        split_func = impurity_split

    random.seed(seed)
    root = DTNode(dataset.labels, dataset.samples, max_depth, split_func)

    split_feature = [None]
    split_value = [None]
    split_left = [None]
    split_right = [None]
    feature_gain = defaultdict(float)

    stack = [(0, root)]

    while stack:
        idx, node = stack.pop()
        if node._leaf:
            split_feature[idx] = None
            split_value[idx] = node._value
            split_left[idx] = None
            split_right[idx] = None
            continue

        split_feature[idx] = node._split_feature
        split_value[idx] = node._split_value
        feature_gain[node._split_feature] += node._gain

        for pointer, child in ((split_left, node._left_child),
                               (split_right, node._right_child)):
            split_feature.append(None)
            split_value.append(None)
            split_left.append(None)
            split_right.append(None)
            stack.append((len(split_feature)-1, child))
            pointer[idx] = len(split_feature)-1

    dt = ('dt', split_feature, split_value, split_left, split_right)
    return ('model', dataset.feature_names, dt), dict(feature_gain)
