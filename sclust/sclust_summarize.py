# -*- coding: utf-8 -*-
"""A command-line tool to print the top clusters output by sclust in a streaming fashion.
E.g., cat data.txt | sclust | sclust-summarize

usage:
    sclust-summarize [--help --frequency <F> --num-docs-to-print <N> --num-clusters-to-print <K>]

Options
    -h, --help
    -f, --frequency <F>               Print clusters every F lines [default: 1000]
    -n, --num-clusters-to-print <N>   Number of top clusters to print [default: 10]
    -k, --num-docs-to-print <K>       Number of documents per cluster to print [default: 1]
"""
from collections import Counter, defaultdict, deque
from docopt import docopt
from math import sqrt, log10
import numpy as np
import re
import sys

def print_summary(cluster_counts, clusterid2lines, num_clusters, lineno):
    print('\n---------%d documents, %d clusters---------\n' % (lineno, len(cluster_counts)))
    for clusterid, count in cluster_counts.most_common(num_clusters):
        lines = clusterid2lines[clusterid]
        print('%d\t%s' % (count, lines[0]))
        for line in list(lines)[1:]:
            print(' \t \t%s' % '\t'.join(line.split('\t')[1:]))
    sys.stdout.flush()

def run(frequency, num_clusters, num_docs):
    cluster_counts = Counter()
    clusterid2lines = defaultdict(lambda: deque(maxlen=num_docs))
    lineno = 0
    for line in sys.stdin:
        line = line.strip()
        lineno += 1
        fields = line.split('\t')
        cluster_counts[fields[0]] += 1
        clusterid2lines[fields[0]].append(line)
        if lineno % frequency == 0:
            print_summary(cluster_counts, clusterid2lines, num_clusters, lineno)
    print_summary(cluster_counts, clusterid2lines, num_clusters, lineno)


# Weirdness when piping to unix tools. See http://stackoverflow.com/a/26736013/1756896
def _void_f(*args,**kwargs):
    pass

def main():
    args = docopt(__doc__)
    try:
        run(int(args['--frequency']), int(args['--num-clusters-to-print']),
            int(args['--num-docs-to-print']))
    except (BrokenPipeError, IOError):
        sys.stdout.write = _void_f
        sys.stdout.flush = _void_f
        sys.exit()



if __name__ == '__main__':
    main()

