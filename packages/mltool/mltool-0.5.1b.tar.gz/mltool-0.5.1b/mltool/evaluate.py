#!/usr/bin/env python
"""
Evaluation functions
--------------------

The metrics considered for the evaluation are two:

- `NDCG`_
- `RMSE`_

.. _`NDCG`: http://en.wikipedia.org/wiki/Discounted_cumulative_gain
.. _`RMSE`: http://en.wikipedia.org/wiki/Mean_squared_error

"""
import math
from itertools import izip, groupby
from operator import itemgetter

import numpy as np

from mltool.predict import predict_all


def dcg(preds, labels):
    order = np.argsort(preds)[::-1]
    preds = np.take(preds, order)
    labels = np.take(labels, order)

    D = np.log2(np.arange(2, len(labels)+2))
    DCG = np.cumsum((2**labels - 1)/D)
    return DCG


def evaluate_preds(preds, dataset, ndcg_at=10):
    """Evaluate predicted value against a labelled dataset.

    :param preds: predicted values, in the same order as the samples in the
                  dataset
    :param dataset: a Dataset object with all labels set
    :param ndcg_at: position at which evaluate NDCG
    :type preds: list-like

    :return: Return the pair RMSE and NDCG scores.

    """
    ndcg = 0.0
    rmse = 0.0
    nqueries = 0
    count = 0

    for _, resultset in groupby(izip(dataset.queries,
                                     preds, dataset.labels),
                                key=itemgetter(0)):
        resultset = list(resultset)
        labels = np.array([l for (_, _, l) in resultset])
        preds = np.array([p for (_, p, _) in resultset])

        rmse += np.sum((labels - preds) ** 2)
        count += len(labels)

        if labels.any():
            ideal_DCG = dcg(labels, labels)
            DCG = dcg(preds, labels)
            k = min(ndcg_at, len(DCG)) - 1
            ndcg += DCG[k] / ideal_DCG[k]
            nqueries += 1
        else:
            ndcg += 0.5
            nqueries += 1

    rmse /= count
    rmse = math.sqrt(rmse)
    ndcg /= nqueries

    return rmse, ndcg


def evaluate_model(model, dataset, ndcg_at=10, return_preds=False):
    """Evaluate a model against a labelled dataset.

    :param model: the model to evaluate
    :param dataset: a Dataset object with all labels set
    :param ndcg_at: position at which evaluate NDCG
    :type preds: list-like

    :return: Return the pair RMSE and NDCG scores.

    """
    preds = predict_all(model, dataset)
    rmse, ndcg = evaluate_preds(preds, dataset, ndcg_at)

    if return_preds:
        return rmse, ndcg, preds
    else:
        return rmse, ndcg
