# -*- coding: utf-8 -*-
"""A command-line tool to quickly cluster sentences.

usage:
    sclust [--help --threshold <T> --update-norms <N>]

Options
    -h, --help
    -t, --threshold <N>    Similarity threshold in [0,1]. Higher means sentences must be more similar to be merged. [default: .2]
"""
from collections import Counter, defaultdict
from docopt import docopt
from math import sqrt, log10
import numpy as np
import re
import sys


def tokenize(line):
    return re.findall('\w+', line.lower())


def idf(token, doc_freqs, docnum):
    return log10((docnum + 1) / doc_freqs[token])


class Cluster:
    def __init__(self, token_counts):
        """
        >>> c = Cluster({'cat': 2, 'dog': 1})
        >>> c.term_scores['cat']  # doctest: +ELLIPSIS
        0.666...
        >>> c.score({'cat': 10}, {'cat': .5})  # doctest: +ELLIPSIS
        3.333...
        >>> c.add({'cat': 3, 'dog': 4})
        >>> c.term_scores['cat']
        0.5
        >>> c.term_scores['dog']
        0.5
        """
        self.term_scores = token_counts
        self.total_tokens = sum(token_counts.values())
        for t, v in token_counts.items():
            self.term_scores[t] = v / self.total_tokens

    def add(self, token_counts):
        new_total_tokens = self.total_tokens + sum(token_counts.values())
        for t, v in self.term_scores.items():
            self.term_scores[t] = ((v * self.total_tokens) + token_counts[t]) / new_total_tokens
        self.total_tokens = new_total_tokens

    def score(self, token_counts, idfs):
        return sum(value * self.term_scores[token] * idfs[token] for token, value in token_counts.items())

def update_index(index, clusterid, tokens):
    for t in tokens:
        index[t].add(clusterid)

def search_index(index, top_words, min_match=2):
    # Require at least min_match terms to match.
    clusters = Counter()
    for w in top_words:
        clusters.update(index[w])
    return [c for c, v in clusters.items() if v >= min_match]

def run(threshold):
    doc_freqs = Counter()
    clusters = []
    docnum = 0
    index = defaultdict(set)
    nmatch = 0
    for line in sys.stdin:
        docnum += 1
        line = line.strip()
        tokens = Counter(tokenize(line))
        if len(tokens) == 0:
            continue
        doc_freqs.update(tokens)
        idfs = {token: idf(token, doc_freqs, docnum) for token in tokens}
        # What are the four words with highest tfidf weight? Use to filter comparisons.
        top_words = sorted(tokens, key=lambda x: -idfs[x])[:4]  # (doc_freqs[token], token) for token in tokens)
        best_cluster = -1
        best_score = -1
        for ci in search_index(index, top_words, min_match=2):
            nmatch += 1
            cluster = clusters[ci]
            score = cluster.score(tokens, idfs)
            if score > best_score and score > threshold:
                best_cluster = ci
                best_score = score
        if best_cluster == -1:
            clusters.append(Cluster(tokens))
            update_index(index, len(clusters)-1, tokens)
            print('%d\t%s\t-' % (len(clusters)-1, line))
        else:
            clusters[best_cluster].add(tokens)
            update_index(index, best_cluster, tokens)
            print('%d\t%s\t%g' % (best_cluster, line, best_score))
        # print('avg num clusters searched per doc=%.1f' % (nmatch / docnum))
        sys.stdout.flush()


# Weirdness when piping to unix tools. See http://stackoverflow.com/a/26736013/1756896
def _void_f(*args,**kwargs):
    pass

def main():
    args = docopt(__doc__)
    try:
        run(float(args['--threshold']))
    except (BrokenPipeError, IOError):
        sys.stdout.write = _void_f
        sys.stdout.flush = _void_f
        sys.exit()



if __name__ == '__main__':
    main()

