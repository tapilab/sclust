# -*- coding: utf-8 -*-
"""A command-line tool to print the top clusters output by sclust in a streaming fashion.
E.g., cat data.txt | sclust | sclust-summarize

usage:
    sclust-summarize [--help --frequency <F> --num-to-print <N>]

Options
    -h, --help
    -f, --frequency <F>      Print clusters every F lines [default: 1000]
    -n, --num-to-print <N>   Number of top clusters to print [default: 10]
"""
from collections import Counter
from docopt import docopt
from math import sqrt, log10
import numpy as np
import re
import sys

def print_summary(cluster_counts, clusterid2line, num_to_print, lineno):
    print('\n---------%d lines---------\n' % lineno)
    for clusterid, count in cluster_counts.most_common(num_to_print):
        print('%d\t%s' % (count, clusterid2line[clusterid]))
    sys.stdout.flush()

def run(frequency, num_to_print):
    cluster_counts = Counter()
    clusterid2line = dict()
    lineno = 0
    for line in sys.stdin:
        line = line.strip()
        lineno += 1
        fields = line.split('\t')
        cluster_counts[fields[0]] += 1
        clusterid2line[fields[0]] = line
        if lineno % frequency == 0:
            print_summary(cluster_counts, clusterid2line, num_to_print, lineno)
    print_summary(cluster_counts, clusterid2line, num_to_print, lineno)


# Weirdness when piping to unix tools. See http://stackoverflow.com/a/26736013/1756896
def _void_f(*args,**kwargs):
    pass

def main():
    args = docopt(__doc__)
    try:
        run(int(args['--frequency']), int(args['--num-to-print']))
    except (BrokenPipeError, IOError):
        sys.stdout.write = _void_f
        sys.stdout.flush = _void_f
        sys.exit()



if __name__ == '__main__':
    main()

