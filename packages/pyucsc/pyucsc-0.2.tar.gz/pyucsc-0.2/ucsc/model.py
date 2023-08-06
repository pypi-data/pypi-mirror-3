from sqlalchemy import sql
from sqlalchemy import orm
from pyfasta import complement

from util import bin
import config

session = None


def make_interval(*args, **kws):
    if not config.genome:
        raise Exception('Fasta file not configured')
    return config.genome.interval(*args, **kws)


class KnownGene(object):
    """ knownGene entry """

    def __repr__(self):
        return "KnownGene(%s, %s, %s:%s-%s)" % (self.geneSymbol, self.name,
                self.chrom, self.txStart, self.txEnd)

    @orm.reconstructor
    def init_on_load(self):
        self.exonStarts = map(int, self.exonStarts.rstrip(',').split(','))
        self.exonEnds = map(int, self.exonEnds.rstrip(',').split(','))
        self.strand = 1 if self.strand == '+' else -1

    @property
    def exons(self):
        """ return a list of Intervals for each exon"""
        return [
            make_interval(*loc, chrom=self.chrom, strand=self.strand)
            for loc in zip(self.exonStarts, self.exonEnds)
        ]

    @property
    def transcript(self):
        """ return an Interval representing the transcript """
        return make_interval(self.txStart, self.txEnd,
                chrom=self.chrom, strand=self.strand, value=self)

    @property
    def cds(self):
        """ return an Interval representing the CDS """
        return make_interval(self.cdsStart, self.cdsEnd,
                chrom=self.chrom, strand=self.strand, value=self)


class CcdsGene(KnownGene):
    """ ccdsGene entry, same interface as KnownGene """
    def __repr__(self):
        return "CcdsGene(%s, %s:%s-%s)" % (self.name, self.chrom,
                self.txStart, self.txEnd)


class RefGene(KnownGene):
    """ refGene entry, same interface as KnownGene """
    def __repr__(self):
        return "RefGene(%s, %s:%s-%s)" % (self.name, self.chrom,
                self.txStart, self.txEnd)


class KnownCanonical(KnownGene):
    """ canonical genes """
    pass


class Snp(object):
    """ SNP entry """

    table = None

    def __repr__(self):
        return "SNP(%s, %s:%s-%s)" % (self.name, self.chrom,
                self.chromStart, self.chromEnd)

    # TODO: inherit query by interval
    @classmethod
    def for_interval(cls, interval):
        """ Return all snps within an interval """
        query = sql.and_(cls.table.c.chromStart>=interval.start,
            cls.table.c.chromEnd<=interval.end,
            cls.table.c.chrom==interval.chrom,
            cls.table.c.bin==bin(interval.start, interval.end)
        )
        return session.query(cls).filter(query).all()

    @property
    def interval(self):
        """ Get this Snp's interval """
        return make_interval(self.chromStart, self.chromEnd, chrom=self.chrom,
            strand=self.strand, value=self)

    def other_alleles(self):
        """ return the alternate allele (always on the + strand, unlike observed)
        """
        if 'ObservedMismatch' in self.exceptions:
            raise NotImplementedError(
                    'Cannot correct ObservedMismatch exception in SNP')
        if 'ObservedTooLong' in self.exceptions:
            raise NotImplementedError(
                    'Cannot get alleles for a too long observed')

        alleles = self.observed.split('/')
        if self.strand == '-':
            alleles = map(complement, alleles)

        # if self.class_ == 'single':
        return [x for x in alleles if x != self.refUCSC]
        # if self

    def apply(self, interval):
        """ Create the alernate alleles on the given interval

            returns a list of alleles over the interval given
        """
        if self.interval.overlaps(interval) and not self.interval in interval:
            raise NotImplementedError(
                    'Cannot apply SNPs not contained in interval, at the moment')
        assert interval.strand in [None, 1],\
                'Only application to the + strand is supported at the moment'

        alt_seqs = []

        for alt in self.other_alleles():
            alt = alt if alt != '-' else ''
            seq = interval.sequence
            if self.interval in interval:
                start_pivot = self.interval.start - interval.start
                end_pivot = self.interval.end - interval.start
                seq = seq[:start_pivot] + alt + seq[end_pivot:]
            alt_seqs.append(seq)
        return alt_seqs


class CommonSnp(Snp):
    """ SNP entry """
    pass


class QueryByInterval(object):
    # """ Mixin for interval queries """

    #TODO: generalize columns used for lookup
    #TODO: what happens when enclosing matching interval spans different bins?

    @classmethod
    def for_interval(cls, interval):
        """ return all links that overlap the specified interval"""
        clause = sql.and_(
            cls.bin==bin(interval.start, interval.end),
            cls.tStart <= interval.end,
            cls.tEnd >= interval.start,
            cls.tName == interval.chrom,
        )
        return session.query(cls).filter(clause).all()


class ChainSelf(QueryByInterval):
    """ Chainself entry """

    def __repr__(self):
        return "ChainSelf(%s -> %s)" % (self.source, self.dest)

    @property
    def source(self):
        """ Interval of the source of the chain """
        return make_interval(self.tStart, self.tEnd,
                chrom=self.tName, strand=1, value=self)

    @property
    def dest(self):
        """ Interval of the destination of the chain """
        if self.qStrand == '-':
            # The - strand coords are given backwards!
            # https://lists.soe.ucsc.edu/pipermail/genome/2009-June/019173.html
            # TODO: remove dependency on GENOME and use DB
            chr_size = len(config.genome.fasta[self.qName]) + 1 # TODO: why + 1?
            end = chr_size - self.qStart
            start = chr_size - self.qEnd
        else:
            start, end = self.qStart, self.qEnd

        return make_interval(self.qStart, self.qEnd,
                chrom=self.qName, strand=self.qStrand, value=self)


class ChainSelfLink(QueryByInterval):
    """ ChainSelfLink entry """

    # TODO: always load chain when loading chainself

    def __repr__(self):
        return "ChainSelfLink(%s -> %s)" % (self.source, self.qStart)

    @property
    def source(self):
        """ Interval of the source of the chain """
        return make_interval(self.tStart, self.tEnd,
                chrom=self.tName, strand=1, value=self)

    @property
    def dest(self):
        """ Interval of the destination of the chain """
        chain = self.chain

        if chain.qStrand == '-':
            # The - strand coords are given backwards!
            # https://lists.soe.ucsc.edu/pipermail/genome/2009-June/019173.html
            # TODO: remove dependency on GENOME and use DB
            chr_size = len(config.genome.fasta[chain.qName]) + 1 # TODO: why + 1?
            end = chr_size - self.qStart
            start = chr_size - self.qStart - len(self.source)
        else:
            start, end = self.qStart, self.qStart + len(self.source)

        return make_interval(start, end,
                chrom=chain.qName, strand=chain.qStrand, value=self)




