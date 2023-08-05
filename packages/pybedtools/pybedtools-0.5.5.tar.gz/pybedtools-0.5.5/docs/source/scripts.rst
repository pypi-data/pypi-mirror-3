Scripts
=======
:mod:`pybedtools` comes with several scripts that illustrate common use-cases.


In Python 2.7, you can use::

    python -m pybedtools

to get a list of scripts and their description.

Venn diagram scripts
--------------------
There are two scripts for making Venn diagrams, depending on how you'd like the
diagrams to look.  Both simply take 3 BED files as input.  ``venn_gchart.py``
uses the Google Chart API, while ``venn_mpl.py`` uses matplotlib if you have it
installed.

Upon installing :mod:`pybedtools`, these scripts should be available on your
path.  Calling them with the `-h` option will print the help, and using the
`--test` option will run a test, creating a new file `out.png` in the current
working directory.

.. figure:: images/gchart.png
    :width: 300px

    Above: using `--test` with `venn_gchart.py` results in this figure


.. figure:: images/mpl.png
    :width: 500px

    Above: Result of using `--test` with `venn_mpl.py`


Intron/exon classification
--------------------------
The script `intron_exon_reads.py` accepts a GFF file (with introns and exons
annotated) and a BAM file.  When complete, it prints out the number of exonic,
intronic, and both intronic and exonic (i.e., from overlapping genes or
isoforms).  This script is also a good example of how to do use Python's
:mod:`multiprocessing` for parallel computation.

Annotate.py
-----------
The `annotate.py` script extends `closestBed` by classifying features (intron,
exon) that are a distance of 0 away from the query features.

``peak_pie.py``
---------------
usage::
    
    peak_pie.py [-h] [--bed BED] [--gff GFF] [--out OUT] [--stranded]
                   [--include [INCLUDE [INCLUDE ...]]]
                   [--exclude [EXCLUDE [EXCLUDE ...]]] [--thresh THRESH]
                   [--test]

Make a pie chart where peaks fall in annotations, similar to CEAS
(http://liulab.dfci.harvard.edu/CEAS/)

However, multi-featuretype classes are reported.  That is, if a peak falls in
an exon in one isoform and an intron in another isoform, the class is "exon,
intron".

optional arguments:
  -h, --help                           show this help message and exit
  --bed BED                            BED file of e.g. peaks
  --gff GFF                            GFF file of e.g. annotations
  --out OUT                            Output PNG file
  --stranded                           Use strand-specific intersections
  --include INCLUDEINCLUDE             Featuretypes to include
  --exclude EXCLUDEEXCLUDE             Featuretypes to exclude
  --thresh THRESH                      Threshold percentage below which output will be suppressed
  --test                               Run test, overwriting all other args. Result will be
                                       "out.png" in current directory.

