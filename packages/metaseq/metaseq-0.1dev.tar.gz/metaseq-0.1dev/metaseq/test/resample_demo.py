#!/usr/bin/python

"""
Example script to explore the behavior of scipy.signal.resample over different
gene lengths and different downsampling bins.  This also acts as a visual test
/ proof-of-principle of MetaChip's meta-gene functionality.
"""

import numpy as np
from matplotlib import pyplot as plt
from scipy.signal import resample


plt.rcParams['legend.fontsize'] = 10

# Figure 1: Constant gene size, but different downsamplings
fig0 = plt.figure(figsize=(10,3))
ax0 = fig0.add_subplot(111)
fig0.subplots_adjust(top=0.8, bottom=0.2)
n = 1000
x0 = np.arange(n)
x = np.linspace(-2 * np.pi, 2 * np.pi, n)
y = np.sin(x) + np.random.rand(n)
ax0.plot(x0, y, '.-', linewidth=3, alpha=0.1, label='original, %sbp' % n)

for ds in [10, 20, 100]:
    y1, x1 = resample(y, ds, x0)
    l, = ax0.plot(x1, y1, '.-', linewidth=1, label=str(ds) + ' bins')
    color = l.get_color()

    # Try to calculate where the truncation happens....(empirically determined)
    ax0.axvline(n - n / ds, color=color, linestyle='--')

ax0.legend(loc='best')
ax0.set_title('Original gene of length `n`, downsampled;\n downsampling to '
              '`ds` bins results in the loss of (n/ds) values',
              fontsize=10)
ax0.set_xlabel('bp')
ax0.set_ylabel('simulated coverage')

# Figures 2 and 3: different gene sizes, same number of bins.  This is what the
# meta-gene functionality will do

# Number of bins
ds = 100

fig1 = plt.figure(figsize=(10,3))
ax1 = fig1.add_subplot(111)
fig2 = plt.figure(figsize=(10,3))
ax2 = fig2.add_subplot(111)

fig1.subplots_adjust(top=0.8, bottom=0.2)
fig2.subplots_adjust(top=0.8, bottom=0.2)

# Iterate over gene sizes
biglist = []
for n in [100, 300, 500, 1000]:
    x = np.linspace(-2 * np.pi, 2 * np.pi, n)
    y = np.sin(x) + np.random.rand(n)
    x0 = np.arange(n)
    ax1.plot(x0, y, '.-', alpha=0.5, label=str(n) + ' bp')
    y1, x1 = resample(y, ds, x0)
    biglist.append(y1)
    #
    # x1 contains the genomic coords, but we want to plot over bins
    ax2.plot(np.arange(ds), y1, '.-', label=str(n) + ' bp', alpha=0.5)

# Plot average -- the average across 1000 meta-genes should get a nice, smooth
# sine curve
ax2.plot(
            np.arange(ds),
            np.array(biglist).mean(axis=0),
            color='k',
            linewidth=10, alpha=0.1, label='average'
        )

ax1.legend(loc='best')
ax2.legend(loc='best')
ax1.set_title('Original genes;\n length varies but pattern is the same',
              fontsize=10)
ax1.set_xlabel('bp')
ax1.set_ylabel('simulated coverage')
ax2.set_title('Meta genes;\ndownsampled to %s bins' % ds, fontsize=10)
ax2.set_xlabel('bins')
ax2.set_ylabel('simulated coverage')

plt.show()
