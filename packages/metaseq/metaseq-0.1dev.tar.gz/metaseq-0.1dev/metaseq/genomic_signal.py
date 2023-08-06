"""
The classes in this module enable random access to a variety of file formats
(BAM, bigWig, bigBed, BED) using a uniform syntax, and allow you to compute
coverage across many features in parallel or just a single feature.

Using classes in the :mod:`metaseq.integration` and :mod:`metaseq.minibrowser`
modules, you can connect these objects to matplotlib figures that show a window
into the data, making exploration easy and interactive.

Generally, the :func:`genomic_signal` function is all you need -- just provide
a filename and the format and it will take care of the rest, returning
a genomic signal of the proper type.

Adding support for a new format is straightforward:

    * Write a new adapter for the format in :mod:`metaseq.filetype_adapters`
    * Subclass one of the existing classes below, setting the `adapter`
      attribute to be an instance of this new adapter
    * Add the new class to the `_registry` dictionary to enable support for the
      file format.

Note that to support parallel processing and to avoid repeating code, these
classes delegate their local_coverage methods to the
:func:`metaseq.array_helpers._local_coverage` function.
"""

import os
import sys
import subprocess

import numpy as np
from bx.bbi.bigwig_file import BigWigFile

from array_helpers import _array, _array_parallel, _local_coverage, \
    _local_coverage_bigwig, _local_count
import filetype_adapters


def supported_formats():
    """
    Returns list of formats supported by metaseq's genomic signal objects.
    """
    return _registry.keys()


def genomic_signal(fn, kind='bam'):
    """
    Factory function that makes the right class for the file format.

    Typically you'll only need this function to create a new genomic signal
    object.

    :param fn: Filename
    :param kind: String.  Format of the file; see metaseq.genomic_signal._registry.keys()
    """
    try:
        klass = _registry[kind.lower()]
    except KeyError:
        raise ValueError('No support for %s format, choices are %s' \
                % (kind, _registry.keys()))
    m = klass(fn)
    m.kind = kind
    return m


class BaseSignal(object):
    """
    Base class to represent objects from which genomic signal can be
    calculated/extracted.

    `__getitem__` uses the underlying adapter the instance was created with
    (e.g., :class:`metaseq.filetype_adapters.BamAdapter` for
    a :class:`BamSignal` object).
    """
    def __init__(self, fn):
        self.fn = fn

    def array(self, features, processes=None, chunksize=None, **kwargs):
        """
        Creates an MxN NumPy array of genomic signal for the region defined by
        each feature in `features`, where M=len(features) and N=bins.

        :param features:
            An iterable of pybedtools.Interval objects

        :param processes:
            Integer or None. If not None, then create the array in
            parallel, giving each process chunks of length `chunksize` to work
            on.

        :param chunksize:
            Integer.  `features` will be split into `chunksize` pieces, and
            each piece will be given to a different process. The optimum value
            is dependent on the size of the features and the underlying data
            set, but `chunksize=100` is a good place to start.

        Additional keyword args are passed to local_coverage() which performs
        the work for each feature; see that method for more details.
        """
        if processes is not None:
            return _array_parallel(
                    self.fn, self.__class__, features, processes=processes,
                    chunksize=chunksize, **kwargs)
        else:
            return _array(self.fn, self.__class__, features, **kwargs)

    def __getitem__(self, key):
        return self.adapter[key]


class BigWigSignal(BaseSignal):
    def __init__(self, fn):
        """
        Class for operating on bigWig files
        """
        BaseSignal.__init__(self, fn)
        self.bigwig = BigWigFile(open(fn))
        import warnings
        warnings.warn('BigWigSignal not well supported '
                      '-- please test and submit bug reports')

    def local_coverage(self, *args, **kwargs):
        return _local_coverage_bigwig(self.bigwig, *args, **kwargs)

    local_coverage.__doc__ = _local_coverage_bigwig.__doc__


class IntervalSignal(BaseSignal):
    def __init__(self, fn):
        """
        Abstract class for bed, BAM and bigBed files.
        """
        BaseSignal.__init__(self, fn)

    def local_coverage(self, *args, **kwargs):
        return _local_coverage(self.adapter, *args, **kwargs)

    def local_count(self, *args, **kwargs):
        return _local_count(self.adapter, *args, **kwargs)

    local_coverage.__doc__ = _local_coverage.__doc__
    local_count.__doc__ = _local_count.__doc__


class BamSignal(IntervalSignal):
    def __init__(self, fn):
        """
        Class for operating on BAM files.
        """
        BaseSignal.__init__(self, fn)
        self._readcount = None
        self.adapter = filetype_adapters.BamAdapter(self.fn)

    def genome(self):
        """
        "genome" dictionary ready for pybedtools, based on the BAM header.
        """
        # This gets the underlying pysam Samfile object
        f = self.adapter.fileobj
        d = {}
        for ref, length in zip(f.references, f.lengths):
            d[ref] = (0, length)
        return d

    def million_mapped_reads(self, force=False):
        """
        Counts total reads in a BAM file and returns the result in millions of
        reads.

        If a file self.bam + '.scale' exists, then just read the first line of
        that file that doesn't start with a "#".  If such a file doesn't exist,
        then it will be created with the number of reads as the first and only
        line in the file.

        The result is also stored in self._readcount so that the time-consuming
        part only runs once; use force=True to force re-count.
        """
        # Already run?
        if self._readcount and not force:
            return self._readcount

        if os.path.exists(self.fn + '.scale') and not force:
            for line in open(self.fn + '.scale'):
                if line.startswith('#'):
                    continue
                self._readcount = float(line.strip())
                return self._readcount

        cmds = ['samtools',
                'view',
                '-c',
                '-F', '0x4',
                self.fn]
        p = subprocess.Popen(cmds, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        if stderr:
            sys.stderr.write('samtools says: %s' % stderr)
            return None
        mmr = int(stdout) / 1e6

        # write to file so the next time you need the lib size you can access
        # it quickly
        if not os.path.exists(self.fn + '.scale'):
            fout = open(self.fn + '.scale', 'w')
            fout.write(str(mmr) + '\n')
            fout.close()

        self._readcount = mmr
        return self._readcount


class BigBedSignal(IntervalSignal):
    def __init__(self, fn):
        """
        Class for operating on bigBed files.
        """
        IntervalSignal.__init__(self, fn)
        self.adapter = filetype_adapters.BigBedAdapter(fn)


class BedSignal(IntervalSignal):
    def __init__(self, fn):
        """
        Class for operating on BED files.
        """
        IntervalSignal.__init__(self, fn)
        self.adapter = filetype_adapters.BedAdapter(fn)


_registry = {
        'bam': BamSignal,
        'bed': BedSignal,
     'bigwig': BigWigSignal,
     'bigbed': BigBedSignal,
     }
