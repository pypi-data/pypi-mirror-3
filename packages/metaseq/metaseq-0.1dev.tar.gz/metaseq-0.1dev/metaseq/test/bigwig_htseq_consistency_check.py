"""
Speed test and consistency check between HTSeq method and bigWig methods of
computing coverage.

Computes coverage for `limit` genes and plots how bigWig sees them compared to
HTSeq.  The fragment size provided to the HTSeq method should reflect tagsize,
not fragment size, to best replicate the bigWig results.

Notes:

    * Based on these tests, HTSeq can be anywhere from 1.5x to 5x faster than
      bigWig

    * scipy.signal.resample uses a Fourier approach, which seems to be pretty
      solid
"""
from pylab import *
import metaseq
import os
import sys
import gffutils
import time

# How many genes to use
limit = 100

sys.stderr.write('Calculating local coverage using HTSeq method and bigWig method.\n')
sys.stderr.write('Compares on-the-fly performance of the two methods, and at the '
                 'end, shows a plot of the TSSs +/- 1kb of the first %s genes.\n' % limit)


# For getting genes...
gfffn = '/DATA/flybase-gff/dmel-all-r5.33-cleaned.gff.db'
G = gffutils.FeatureDB(gfffn)

bam = metaseq.example_filename('sh_chr2L.bam')
bigwig = metaseq.example_filename('sh_chr2L.bigwig')

# Make a bigwig if it's not available
if not os.path.exists(bigwig):
    metaseq.helpers.bam2bigwig(bam=bam, bigwig=bigwig, genome='dm3', verbose=True, scale=1e6)

# How far past gene boundaries to get
extend = 1000


# number of bins to use
nbins = 200


m0 = metaseq.metaseq(bam, fragmentsize=36)
m1 = metaseq.BigWigmetaseq(bigwig, nbins=nbins)


# These will accumulate averages.
# In general, vars' suffixes are
#   0 = htseq
#   1 = bigwig
z0 = np.zeros( (nbins,) )
z1 = np.zeros( (nbins,) )

# Total elapsed
te0 = 0.
te1 = 0.

c = 0
while 1:
    g = G.random_feature('gene')
    if not g.chrom == 'chr2L':
        continue
    c += 1
    c += 1
    if c > limit:
        break

    t0 = time.time()
    x0, y0 = m0.local_coverage(g.chrom, g.TSS-extend, g.TSS+extend, g.strand, bins=nbins)
    z0 += y0 / limit
    e0 = time.time() - t0

    t1 = time.time()
    x1, y1 = m1.local_coverage(g.chrom, g.TSS-extend, g.TSS+extend, g.strand)
    z1 += y1 / limit
    e1 = time.time() - t1

    sys.stderr.write('\r%s -- %00.1fkb (htseq = %.2fx faster )' % (c, len(g)/1000., e1/e0))
    sys.stderr.flush()
    te0 += e0
    te1 += e1

fig = figure()
ax = fig.add_subplot(111)

# plot normalized, cause fragmentsize extension will change absolute values
ax.plot(arange(nbins), z0/z0.max(), label='htseq')
ax.plot(arange(nbins), z1/z1.max(), label='bigwig')
ax.legend(loc='best')
print 'total htseq speedup: %.1fx' % (te1/te0)
ax.axis('tight')
show()
