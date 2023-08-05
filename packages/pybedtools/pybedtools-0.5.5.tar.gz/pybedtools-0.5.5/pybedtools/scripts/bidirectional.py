#!/usr/bin/python
"""
Given a GFF file, returns a BED file of the [possibly merged] space between
bidirectional promoters
"""
import sys
import argparse
import pybedtools


def featurefilt(feature, featuretype='mRNA', exclude_chroms=None):
    """
    Filter function to pass only features of `featuretype` and that do not have
    chroms in `exclude_chroms`.
    """
    if exclude_chroms is None:
        return feature[2] == featuretype
    else:
        return (feature[2] == featuretype) and \
                (feature.chrom not in exclude_chroms)


def TSS(feature):
    """
    Converts a feature into a TSS with length 1 bp
    """
    if feature.strand == '-':
        tss = feature.stop
    else:
        tss = feature.start
    feature.start = tss
    feature.stop = tss + 1
    return feature


def inter(x):
    """
    Given a feature line of 2 concatenated GFF features, returns a new BED
    feature containing the intervening space.
    """
    start1 = int(x[3])
    stop1 = int(x[4])
    stop2 = int(x[13])
    start2 = int(x[12])
    chrom = x.chrom
    if start1 < start2:
        start = start1
        stop = start2
    else:
        start = start2
        stop = start1
    return pybedtools.create_interval_from_list(
            [chrom, str(start), str(stop)])


def between_bidirectional_promoters(gff, exclude=None, featuretype='mRNA',
        window=1000):
    """
    Finds promoters of `featuretype` features from GFF file `gff` on opposite
    strands that are within `window` bp apart and prints the merged intervening
    space as BED3 features.
    """
    features = pybedtools.BedTool(gff)
    filtered = features.filter(featurefilt, featuretype, exclude)
    tsses = filtered.each(TSS).saveas()
    plus_tss = tsses.filter(lambda x: x.strand == '+').saveas()
    minus_tss = tsses.filter(lambda x: x.strand == '-').saveas()
    bi = plus_tss.window(minus_tss, Sm=True, w=window)
    for feature in bi.each(inter).merge():
        sys.stdout.write(str(feature) + '\n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--gff', help='GFF file containing featuretypes')
    ap.add_argument('--featuretype', '-f', default='mRNA',
                    help='Featuretype to get TSS from; default is mRNA')
    ap.add_argument('-w', type=int, default=1000, help='Window, in bp, within '
                    'which an opposite-strand promoter will be considered a '
                    'neighbor; default=1000')
    ap.add_argument('--exclude-chroms', nargs="*", dest='exclude',
                    help='Comma-separated list of chromosomes to exclude.')
    args = ap.parse_args()
    between_bidirectional_promoters(
            gff=args.gff,
            exclude=args.exclude,
            featuretype=args.featuretype,
            window=args.w)

if __name__ == "__main__":
    main()
