"""
Prediction functions
--------------------

:mod:`predict <mltool.predict>` contains functions to predict the target
variable score given a model.

"""
from collections import Mapping

import numpy as np


def _raw_predict(model, sample):
    """Compute the predicted target variable score for the given sample

    Expect the features to be already ordered.

    """
    idx = 0
    if model[0] == 'model':
        return _raw_predict(model[2], sample)
    if model[0] == 'dt':
        split_feature, split_value, split_left, split_right = model[1:]

        while split_feature[idx] is not None:
            if sample[split_feature[idx]] <= split_value[idx]:
                idx = split_left[idx]
            else:
                idx = split_right[idx]

        return split_value[idx]
    elif model[0] == 'avg':
        value = 0.0
        for submodel in model[1:]:
            value += _raw_predict(submodel, sample)
        return value / (len(model) - 1)
    elif model[0] == 'sum':
        value = 0.0
        for submodel in model[1:]:
            value += _raw_predict(submodel, sample)
        return value
    else:
        assert False, 'Unknown model format'


def predict(model, sample):
    """Predict the score of a sample

    :param model: the prediction model
    :param sample: a dictionary/namedtuple with all the features required
                   by the model

    :return: return the predicted score

    """
    assert model[0] == 'model'

    if isinstance(sample, Mapping):
        get = lambda o, k: o[k]
    else:
        get = getattr

    try:
        reorder_sample = np.array([get(sample, k) for k in model[1]])
    except KeyError as e:
        raise KeyError('Missing feature %s in the sample' % e.args[0])

    return _raw_predict(model[2], reorder_sample)


def predict_all(model, dataset):
    """Predict targets for each sample in the dataset

    :param model: the prediction model
    :param dataset: a dataset

    :return: return the predicted scores

    """
    samples = dataset.samples
    feature_order = dataset.feature_names

    if model[0] != 'model':
        import warnings
        warnings.warn('Missing feature ordering in the model: '
                      'use dataset order')

    return _predict_all(model, samples, feature_order)


def _reorder_features(samples, curr_order, new_order):
    """Change feature ordering

    """
    curr_order_map = dict((v, k) for k, v in enumerate(curr_order))
    try:
        new_order_indices = [curr_order_map[k] for k in new_order]
    except KeyError as e:
        raise KeyError('Missing feature %s in the dataset' % e.args[0])

    return (np.take(samples, new_order_indices, axis=0), new_order)


def _predict_all(model, samples, feature_order):
    """Low-level function for predict scores in a sample set

    """
    if model[0] == 'model':
        samples, feature_order = _reorder_features(samples,
                                                   feature_order,
                                                   model[1])
        return _predict_all(model[2], samples, feature_order)
    elif model[0] == 'dt':
        split_feature, split_value, split_left, split_right = model[1:]
        stack = [(0, np.arange(samples.shape[1]))]
        preds = np.empty(samples.shape[1])

        while stack:
            node, indices = stack.pop()
            if split_feature[node] is None:
                preds[indices] = split_value[node]
            else:
                cond = samples[split_feature[node],
                               indices] <= split_value[node]
                left_indices = indices[cond]
                right_indices = indices[~cond]
                stack.append((split_left[node],
                              left_indices))
                stack.append((split_right[node],
                              right_indices))

        return preds
    elif model[0] in ('avg', 'sum'):
        acc = np.zeros(samples.shape[1])
        for submodel in model[1:]:
            acc += _predict_all(submodel, samples, feature_order)
        if model[0] == 'avg':
            acc /= len(model) - 1
        return acc
    else:
        assert False, 'Unknown model format'
