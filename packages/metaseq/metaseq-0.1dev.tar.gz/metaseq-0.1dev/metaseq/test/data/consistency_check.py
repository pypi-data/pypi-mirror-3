import metachip
from pylab import *
import pybedtools

f = pybedtools.create_interval_from_list(['chr2L', '5600', '6000'])
bins = 500

bam = metachip.create_metachip('sh_chr2L.bam', kind='bam')
bed = metachip.create_metachip('sh_chr2L.bed.gz', kind='bed')


fig = figure()
ax1 = fig.add_subplot(211)
ax2 = fig.add_subplot(212, sharex=ax1)
ax1.plot(*bam.local_coverage(f, bins=bins), color='b')
ax2.plot(*bed.local_coverage(f, bins=bins, use_score=True), color='r')
show()
