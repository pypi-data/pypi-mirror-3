import pybedtools
reads = pybedtools.example_bedtool('gdc.bam')
genes = pybedtools.example_bedtool('gdc.gff')
for read in reads:
    for gene in genes.all_hits(read):
        print repr(read), gene.name
