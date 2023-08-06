from collections import namedtuple
from itertools import izip

import numpy as np


Dataset = namedtuple('Dataset', 'labels queries samples feature_names')


def read_input_file(fin):
    """Read a dataset from a file

    :param fin: a file-like object to read the dataset from
    :return: a :class:`Dataset` object.

    """
    header = next(fin)
    header = header.split()
    header_dict = dict((k, v) for (v, k) in enumerate(header))
    feature_names = tuple(k for k in header if not k.endswith('_'))
    feature_idx = [idx for idx, k in enumerate(header) if not k.endswith('_')]

    rows = []
    labels = []
    queries = []
    try:
        query_idx = header_dict['qid_']
        label_idx = header_dict['label_']
    except KeyError:
        raise ValueError('expected qid_ and label_ columns, '
                         'wrong file format?')

    for row in fin:
        row, _, _ = row.partition('#')
        row = row.split()
        f_values = np.array([float(row[x]) for x in feature_idx])
        rows.append(f_values)
        queries.append(int(row[query_idx]))
        labels.append(float(row[label_idx]))

    samples = np.array(rows).T
    labels = np.array(labels)
    queries = np.array(queries)
    return Dataset(labels, queries, samples, feature_names)


def write_dataset(fout, dataset):
    header = ['qid_', 'label_'] + dataset.feature_names
    print >>fout, '%s' % '\t'.join(header)
    for qid, label, row in izip(dataset.queries, dataset.labels,
                                dataset.samples.T):
        print >>fout, '%s\t%r\t%s' % (qid, label,
                                      '\t'.join('%r' % v for v in row))


def read_input_file_svmrank(fin):
    labels = []
    queries = []
    samples = []

    max_feat_idx = 0

    for row in fin:
        row = row.partition('#')[0]
        row = row.split()
        if not row:
            continue

        labels.append(float(row[0]))
        query_id = int(row[1].split(':')[-1])
        queries.append(query_id)
        vec = {}
        for f in row[2:]:
            f_id, f_value = f.split(':')
            f_id = int(f_id)
            f_value = float(f_value)

            assert f_id > 0, 'Feature ID must be a positive number >0'
            vec[f_id] = f_value
            max_feat_idx = max(f_id, max_feat_idx)

        samples.append(vec)

    # convert to numpy array
    labels = np.array(labels, dtype=float)
    queries = np.array(queries, dtype=int)
    sample_array = np.zeros((max_feat_idx, len(labels)))
    for i, u in enumerate(samples):
        for f_id, f_value in u.iteritems():
            sample_array[f_id-1, i] = f_value

    feature_names = [('f%d' % i) for i in xrange(sample_array.shape[0])]

    return Dataset(labels, queries, sample_array, feature_names)


def sample_dataset(dataset):
    # TODO: maybe we want to sample only by queries...

    N = len(dataset.labels)
    indices = np.random.randint(N, size=N)
    labels = np.take(dataset.labels, indices)
    queries = np.take(dataset.queries, indices)
    samples = np.take(dataset.samples, indices, axis=1)

    return Dataset(labels, queries, samples, dataset.feature_names)
