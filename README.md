# sclust
simple sentence clusterer

A tool to cluster lines of text in a streaming fashion.

E.g., if you have a file like this, with one sentence per line:

```
$ cat /tmp/foo
Hi there, how are you?
hi where how you are
i like to sing
I am going to sing
hi where how you are
hi there how...
do you sing???
```

You can pipe it to `sclust` to get cluster assignments:

```
$ cat /tmp/foo | sclust
0	Hi there, how are you?	-
0	hi where how you are	0.352689
1	i like to sing	-
1	I am going to sing	0.401597
0	hi where how you are	0.82069
0	hi there how...	0.45287
2	do you sing???	-
```
Here, the first column is the cluster assignment and the third column is the cosine similarity between that line and the cluster it is assigned to. The algorithm is online (as opposed to batch), so order matters. At each iteration, a document is assigned to its closest cluster, according to cosine similarity.

Other options:
```
$ sclust --help
A command-line tool to quickly cluster sentences.

usage:
    sclust [--help --threshold <T> --update-norms <N>]

Options
    -h, --help
    -t, --threshold <N>    Similarity threshold in [0,1]. Higher means sentences must be more similar to be merged. [default: .2]
    -u, --update-norms <N>    Update cluster norms every N documents. Larger values reduce run-time, but sacrifice accuracy. [default: 1]
```

There is also a tool `sclust-summarize` to view the output.

$ sclust-summarize --help
A command-line tool to print the top clusters output by sclust in a streaming fashion.
E.g., cat data.txt | sclust | sclust-summarize

```
usage:
    sclust-summarize [--help --frequency <F> --num-docs-to-print <N> --num-clusters-to-print <K>]

Options
    -h, --help
    -f, --frequency <F>               Print clusters every F lines [default: 1000]
    -n, --num-clusters-to-print <N>   Number of top clusters to print [default: 10]
    -k, --num-docs-to-print <K>       Number of documents per cluster to print [default: 1]
```

E.g.,

```
$ cat /tmp/foo | sclust | sclust-summarize  -k 3

---------7 documents, 3 clusters---------

4	0	hi where how you are	0.352689
 	 	hi where how you are	0.82069
 	 	hi there how...	0.45287
2	1	i like to sing	-
 	 	I am going to sing	0.401597
1	2	do you sing???	-
```

The nice thing is you can pipe a large file and see the clusters change as documents are read. E.g., 

```
$  cat /tmp/a_bunch_of_tweets  | sclust -t .2 -u 1000 | sclust-summarize -k 2 -n 5 

---------1000 documents, 715 clusters---------

15	68	lol	0.73664
 	 	i need matching jewelry me lj lol	0.215373
9	93	if you love watching huge zits getting popped then you re gonna love this it like therapeutic for me webaddress	0.273418
 	 	i love jesus exclamationpoint	0.314281
9	324	no one going to pay for content what they used to pay doesn t matter what it is	0.29804
 	 	what	0.646988
9	14	studing exclamationpoint studing exclamationpoint oh sh	0.23397
 	 	oh yeah this woman knows what she talkin about exclamationpoint	0.232043
7	160	rt	0.615143
 	 	rt plz rt fast waystation needs help evacuating animals exclamationpoint now exclamationpoint little tujunga canyon rt	0.269342

---------2000 documents, 1209 clusters---------

21	98	comendo happyemoticon	0.281718
 	 	we are better now and for good this time happyemoticon i love her happyemoticon	0.378463
19	68	lol who da hell u talkin bout	0.202604
 	 	see lol	0.448003
17	93	i love it here	0.512499
 	 	i love target and my lovelies	0.254959
16	14	oh yeah exclamationpoint lol	0.566714
 	 	uh oh	0.391978
15	135	lol i love hey arnold	0.642059
 	 	hey diggy	0.357601

---------3000 documents, 1621 clusters---------

29	93	i love you baby sister	0.349325
 	 	i love you diva o	0.366829
28	98	and im luvin it happyemoticon	0.263552
 	 	heyy everyone happyemoticon how are ya	0.225831
27	68	lol well i txt her just put jessica hahaha	0.207772
 	 	my bad i was falling myself lol	0.262167
25	135	and ahh exclamationpoint i love hey arnold exclamationpoint	0.599761
 	 	hey happyemoticon its exclamationpoint	0.53119
21	14	oh psych how you make my day	0.335252
 	 	oh my god oh my god oh my god	0.556064
```
