# -*- coding: utf-8 -*-
"""A command-line tool to quickly cluster sentences.

usage:
    sclust [--help --batch <B> --threshold <T>]

Options
    -h, --help
    -b, --batch <N>        Cluster in batches of this size. [default: 10]
    -t, --threshold <N>    Similarity threshold in [0,1]. Higher means sentences must be more similar to be merged. [default: .8]
"""
from collections import Counter
from docopt import docopt
from math import sqrt, log10
import numpy as np
import re
import sys


def norm(tokens, doc_freqs, docnum):
    return sqrt(np.sum((count * idf(token, doc_freqs, docnum))**2
                       for token, count in tokens.items()))


def tokenize(line):
    return re.findall('\w+', line.lower())


def idf(token, doc_freqs, docnum):
    return log10((docnum + 1) / doc_freqs[token])

class Cluster:
    def __init__(self, token_counts):
        self.token_counts = Counter(token_counts)

    def add(self, tokens):
        self.token_counts.update(tokens)

    def score(self, tokens, doc_norm, doc_freqs, docnum):
        cluster_norm = norm(self.token_counts, doc_freqs, docnum)
        numer = 0
        for token, count in tokens.items():
            numer += self.token_counts[token] * count * idf(token, doc_freqs, docnum)**2
        return numer / (cluster_norm * doc_norm)


def run(batch_size, threshold):
    doc_freqs = Counter()
    clusters = []
    docnum = 0
    for line in sys.stdin:
        docnum += 1
        line = line.strip()
        tokens = Counter(tokenize(line))
        doc_freqs.update(tokens)
        this_norm = norm(tokens, doc_freqs, docnum)
        # What is the word with highest tfidf weight? Used to filter comparisons.
        top_words = sorted((doc_freqs[token], token) for token in tokens if doc_freqs[token] > 1)
        top_words = set(w[1] for w in top_words[:3])
        best_cluster = -1
        best_score = -1
        for ci, cluster in enumerate(clusters):
            if len(top_words) == 0 or len(top_words & set(cluster.token_counts)) > 0:
                score = cluster.score(tokens, this_norm, doc_freqs, docnum)
                if score > best_score and score > threshold:
                    best_cluster = ci
                    best_score = score
        if best_cluster == -1:
            clusters.append(Cluster(tokens))
            print('%d\t%s\tNA' % (len(clusters)-1, line))
        else:
            clusters[best_cluster].add(tokens)
            print('%d\t%s\t%g' % (best_cluster, line, best_score))
        sys.stdout.flush()


# Weirdness when piping to unix tools. See http://stackoverflow.com/a/26736013/1756896
def _void_f(*args,**kwargs):
    pass

def main():
    args = docopt(__doc__)
    try:
        run(int(args['--batch']), float(args['--threshold']))
    except (BrokenPipeError, IOError):
        sys.stdout.write = _void_f
        sys.stdout.flush = _void_f
        sys.exit()



if __name__ == '__main__':
    main()

