# -*- coding: utf-8 -*-
"""A command-line tool to quickly cluster sentences.

usage:
    sclust [--help --threshold <T> --update-norms <N> --prune-frequency <P>]

Options
    -h, --help
    -p, --prune-frequency <P>   Delete small clusters every P lines [default: -1]
    -t, --threshold <N>         Similarity threshold in [0,1]. Higher means sentences must be more similar to be merged. [default: .2]
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
    def __init__(self, _id, token_counts):
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
        self._id = _id
        self.size = 1
        self.term_scores = token_counts
        self.total_tokens = sum(token_counts.values())
        for t, v in token_counts.items():
            self.term_scores[t] = v / self.total_tokens

    def __hash__(self):
        return self._id

    def add(self, token_counts):
        new_total_tokens = self.total_tokens + sum(token_counts.values())
        for t, v in self.term_scores.items():
            self.term_scores[t] = ((v * self.total_tokens) + token_counts[t]) / new_total_tokens
        self.total_tokens = new_total_tokens
        self.size += 1

    def score(self, token_counts, idfs):
        return sum(value * self.term_scores[token] * idfs[token] for token, value in token_counts.items())

def update_index(index, cluster, tokens):
    for t in tokens:
        index[t].add(cluster)

def search_index(index, top_words, min_match=2):
    # Require at least min_match terms to match.
    clusters = Counter()
    for w in top_words:
        clusters.update(index[w])
    return [c for c, v in clusters.items() if v >= min_match]

def prune_clusters(clusters, index, n=3):
    """
    Delete clusters with fewer than n elements.
    """
    torem = set(c for c in clusters if c.size < n)
    pruned_clusters = [c for c in clusters if c.size >= n]
    terms_torem = []
    for term, clusters in index.items():
        index[term] = clusters - torem
        if len(index[term]) == 0:
            terms_torem.append(term)
    for t in terms_torem:
        del index[t]
    return pruned_clusters, index

def run(threshold, prune_freq):
    cluster_count = 0
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
        best_cluster = None
        best_score = -1
        for cluster in search_index(index, top_words, min_match=2):
            nmatch += 1
            # cluster = clusters[ci]
            score = cluster.score(tokens, idfs)
            if score > best_score and score > threshold:
                best_cluster = cluster
                best_score = score
        if not best_cluster:
            new_cluster = Cluster(cluster_count, tokens)
            clusters.append(new_cluster)
            # clusters.append(Cluster(cluster_count, tokens))
            # update_index(index, cluster_count, tokens)
            # print('%d\t%s\t-' % (cluster_count, line))
            update_index(index, new_cluster, tokens)
            print('%d\t%s\t-' % (new_cluster._id, line))
            cluster_count += 1
        else:
            #clusters[best_cluster].add(tokens)
            best_cluster.add(tokens)
            update_index(index, best_cluster, tokens)
            print('%d\t%s\t%g' % (best_cluster._id, line, best_score))
        if prune_freq != -1 and docnum % prune_freq == 0:
            clusters, index = prune_clusters(clusters, index)

        # print('avg num clusters searched per doc=%.1f' % (nmatch / docnum))
        sys.stdout.flush()


# Weirdness when piping to unix tools. See http://stackoverflow.com/a/26736013/1756896
def _void_f(*args,**kwargs):
    pass

def main():
    args = docopt(__doc__)
    try:
        run(float(args['--threshold']), float(args['--prune-frequency']))
    except (BrokenPipeError, IOError):
        sys.stdout.write = _void_f
        sys.stdout.flush = _void_f
        sys.exit()



if __name__ == '__main__':
    main()

