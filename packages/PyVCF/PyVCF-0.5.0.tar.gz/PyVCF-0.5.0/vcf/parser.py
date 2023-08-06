import collections
import re
import csv
import gzip
import sys
import itertools
import codecs

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

try:
    import pysam
except ImportError:
    pysam = None


# Metadata parsers/constants
RESERVED_INFO = {
    'AA': 'String', 'AC': 'Integer', 'AF': 'Float', 'AN': 'Integer',
    'BQ': 'Float', 'CIGAR': 'String', 'DB': 'Flag', 'DP': 'Integer',
    'END': 'Integer', 'H2': 'Flag', 'MQ': 'Float', 'MQ0': 'Integer',
    'NS': 'Integer', 'SB': 'String', 'SOMATIC': 'Flag', 'VALIDATED': 'Flag',

    # VCF 4.1 Additions
    'IMPRECISE':'Flag', 'NOVEL':'Flag', 'END':'Integer', 'SVTYPE':'String',
    'CIPOS':'Integer','CIEND':'Integer','HOMLEN':'Integer','HOMSEQ':'Integer',
    'BKPTID':'String','MEINFO':'String','METRANS':'String','DGVID':'String',
    'DBVARID':'String','MATEID':'String','PARID':'String','EVENT':'String',
    'CILEN':'Integer','CN':'Integer','CNADJ':'Integer','CICN':'Integer',
    'CICNADJ':'Integer'
}

RESERVED_FORMAT = {
    'GT': 'String', 'DP': 'Integer', 'FT': 'String', 'GL': 'Float',
    'GQ': 'Float', 'HQ': 'Float',

    # VCF 4.1 Additions
    'CN':'Integer','CNQ':'Float','CNL':'Float','NQ':'Integer','HAP':'Integer',
    'AHAP':'Integer'
}

# Spec is a bit weak on which metadata lines are singular, like fileformat
# and which can have repeats, like contig
SINGULAR_METADATA = ['fileformat', 'fileDate', 'reference']

# Conversion between value in file and Python value
field_counts = {
    '.': None,  # Unknown number of values
    'A': -1,  # Equal to the number of alleles in a given record
    'G': -2,  # Equal to the number of genotypes in a given record
}


_Info = collections.namedtuple('Info', ['id', 'num', 'type', 'desc'])
_Filter = collections.namedtuple('Filter', ['id', 'desc'])
_Alt = collections.namedtuple('Alt', ['id', 'desc'])
_Format = collections.namedtuple('Format', ['id', 'num', 'type', 'desc'])
_SampleInfo = collections.namedtuple('SampleInfo', ['samples', 'gt_bases', 'gt_types', 'gt_phases'])


class _AltRecord(object):
    '''An alternative allele record: either replacement string, SV placeholder, or breakend'''

    def __init__(self, type):
        #: String to describe the type of variant, by default "SNV" or "MNV", but can be extended to any of the types described in the ALT lines of the header (e.g. "DUP", "DEL", "INS"...)
        self.type = type

    def __str__(self):
        assert False, "_AltRecord is an abstract class, you should be using a subclass instead"

    def __eq__(self, other):
        return self.type == other.type


class _Substitution(_AltRecord):
    '''A basic ALT record, where a REF sequence is replaced by an ALT sequence'''

    def __init__(self, nucleotides):
        if len(nucleotides) == 1:
            super(_Substitution, self).__init__("SNV")
        else:
            super(_Substitution, self).__init__("MNV")
        #: Alternate sequence
        self.sequence = str(nucleotides)

    def __str__(self):
        return self.sequence

    def __repr__(self):
        return str(self)

    def __len__(self):
        return len(self.sequence)

    def __eq__(self, other):
        if isinstance(other, basestring):
            return self.sequence == other
        else:
            return super(_Substitution, self).__eq__(other) and self.sequence == other.sequence


class _Breakend(_AltRecord):
    '''A breakend which is paired to a remote location on or off the genome'''

    def __init__(self, chr, pos, orientation, remoteOrientation, connectingSequence, withinMainAssembly):
        super(_Breakend, self).__init__("BND")
        #: The chromosome of breakend's mate.
        self.chr = str(chr)
        #: The coordinate of breakend's mate.
        self.pos = int(pos)
        #: The orientation of breakend's mate. If the sequence 3' of the breakend's mate is connected, True, else if the sequence 5' of the breakend's mate is connected, False.
        self.remoteOrientation = remoteOrientation
        #: If the breakend mate is within the assembly, True, else False if the breakend mate is on a contig in an ancillary assembly file.
        self.withinMainAssembly = withinMainAssembly
        #: The orientation of breakend. If the sequence 3' of the breakend is connected, True, else if the sequence 5' of the breakend is connected, False.
        self.orientation = orientation
        #: The breakpoint's connecting sequence.
        self.connectingSequence = connectingSequence

    def __repr__(self):
        return str(self)

    def __str__(self):
        if self.chr is None:
            remoteTag = '.'
        else:
            if self.withinMainAssembly:
                remoteChr = self.chr
            else:
                remoteChr = "<" + self.chr + ">"
            if self.remoteOrientation:
                remoteTag = "[" + remoteChr + ":" + str(self.pos) + "["
            else:
                remoteTag = "]" + remoteChr + ":" + str(self.pos) + "]"

        if self.orientation:
            return remoteTag + self.connectingSequence
        else:
            return self.connectingSequence + remoteTag

    def __eq__(self, other):
        return super(_Breakend, self).__eq__(other) \
                and self.chr == other.chr \
                and self.pos == other.pos \
                and self.remoteOrientation == other.remoteOrientation \
                and self.withinMainAssembly == other.withinMainAssembly \
                and self.orientation == other.orientation \
                and self.connectingSequence == other.connectingSequence


class _SingleBreakend(_Breakend):
    '''A single breakend'''

    def __init__(self, orientation, connectingSequence):
        super(_SingleBreakend, self).__init__(None, None, orientation, None, connectingSequence, None)


class _SV(_AltRecord):
    '''An SV placeholder'''

    def __init__(self, type):
        super(_SV, self).__init__(type)

    def __str__(self):
        return "<" + self.type + ">"

    def __repr__(self):
        return str(self)


class _vcf_metadata_parser(object):
    '''Parse the metadat in the header of a VCF file.'''
    def __init__(self):
        super(_vcf_metadata_parser, self).__init__()
        self.info_pattern = re.compile(r'''\#\#INFO=<
            ID=(?P<id>[^,]+),
            Number=(?P<number>-?\d+|\.|[AG]),
            Type=(?P<type>Integer|Float|Flag|Character|String),
            Description="(?P<desc>[^"]*)"
            >''', re.VERBOSE)
        self.filter_pattern = re.compile(r'''\#\#FILTER=<
            ID=(?P<id>[^,]+),
            Description="(?P<desc>[^"]*)"
            >''', re.VERBOSE)
        self.alt_pattern = re.compile(r'''\#\#ALT=<
            ID=(?P<id>[^,]+),
            Description="(?P<desc>[^"]*)"
            >''', re.VERBOSE)
        self.format_pattern = re.compile(r'''\#\#FORMAT=<
            ID=(?P<id>.+),
            Number=(?P<number>-?\d+|\.|[AG]),
            Type=(?P<type>.+),
            Description="(?P<desc>.*)"
            >''', re.VERBOSE)
        self.meta_pattern = re.compile(r'''##(?P<key>.+?)=(?P<val>.+)''')

    def vcf_field_count(self, num_str):
        """Cast vcf header numbers to integer or None"""
        if num_str not in field_counts:
            # Fixed, specified number
            return int(num_str)
        else:
            return field_counts[num_str]

    def read_info(self, info_string):
        '''Read a meta-information INFO line.'''
        match = self.info_pattern.match(info_string)
        if not match:
            raise SyntaxError(
                "One of the INFO lines is malformed: %s" % info_string)

        num = self.vcf_field_count(match.group('number'))

        info = _Info(match.group('id'), num,
                     match.group('type'), match.group('desc'))

        return (match.group('id'), info)

    def read_filter(self, filter_string):
        '''Read a meta-information FILTER line.'''
        match = self.filter_pattern.match(filter_string)
        if not match:
            raise SyntaxError(
                "One of the FILTER lines is malformed: %s" % filter_string)

        filt = _Filter(match.group('id'), match.group('desc'))

        return (match.group('id'), filt)

    def read_alt(self, alt_string):
        '''Read a meta-information ALTline.'''
        match = self.alt_pattern.match(alt_string)
        if not match:
            raise SyntaxError(
                "One of the FILTER lines is malformed: %s" % alt_string)

        alt = _Alt(match.group('id'), match.group('desc'))

        return (match.group('id'), alt)

    def read_format(self, format_string):
        '''Read a meta-information FORMAT line.'''
        match = self.format_pattern.match(format_string)
        if not match:
            raise SyntaxError(
                "One of the FORMAT lines is malformed: %s" % format_string)

        num = self.vcf_field_count(match.group('number'))

        form = _Format(match.group('id'), num,
                       match.group('type'), match.group('desc'))

        return (match.group('id'), form)

    def read_meta_hash(self, meta_string):
        items = re.split("[<>]", meta_string)
        # Removing initial hash marks and final equal sign
        key = items[0][2:-1]
        hashItems = items[1].split(',')
        val = dict(item.split("=") for item in hashItems)
        return key, val

    def read_meta(self, meta_string):
        if re.match("##.+=<", meta_string):
            return self.read_meta_hash(meta_string)
        else:
            match = self.meta_pattern.match(meta_string)
            return match.group('key'), match.group('val')


class _Call(object):

    __slots__ = ['site', 'sample', 'data', 'gt_nums', 'called']

    """ A genotype call, a cell entry in a VCF file"""
    def __init__(self, site, sample, data):
        #: The ``_Record`` for this ``_Call``
        self.site = site
        #: The sample name
        self.sample = sample
        #: Dictionary of data from the VCF file
        self.data = data
        self.gt_nums = self.data.get('GT')
        #: True if the GT is not ./.
        self.called = self.gt_nums is not None

    def __repr__(self):
        return "Call(sample=%s, GT=%s%s)" % (self.sample, self.gt_nums,
                "".join([", %s=%s" % (X, self.data[X]) for X in self.data if X != 'GT']))

    def __eq__(self, other):
        """ Two _Calls are equal if their _Records are equal
            and the samples and ``gt_type``s are the same
        """
        return (self.site == other.site
                and self.sample == other.sample
                and self.gt_type == other.gt_type)

    def gt_phase_char(self):
        return "/" if not self.phased else "|"

    @property
    def gt_alleles(self):
        '''The numbers of the alleles called at a given sample'''
        # grab the numeric alleles of the gt string; tokenize by phasing
        return self.gt_nums.split(self.gt_phase_char())

    @property
    def gt_bases(self):
        '''The actual genotype alleles.
           E.g. if VCF genotype is 0/1, return A/G
        '''
        # nothing to do if no genotype call
        if self.called:
            # lookup and return the actual DNA alleles
            try:
                return self.gt_phase_char().join(str(self.site.alleles[int(X)]) for X in self.gt_alleles)
            except:
                sys.stderr.write("Allele number not found in list of alleles\n")
        else:
            return None

    @property
    def gt_type(self):
        '''The type of genotype.
           hom_ref  = 0
           het      = 1
           hom_alt  = 2  (we don;t track _which+ ALT)
           uncalled = None
        '''
        # extract the numeric alleles of the gt string
        if self.called:
            alleles = self.gt_alleles
            if all(X == alleles[0] for X in alleles[1:]):
                if alleles[0] == "0": return 0
                else: return 2
            else: return 1
        else: return None

    @property
    def phased(self):
        '''A boolean indicating whether or not
           the genotype is phased for this sample
        '''
        return self.gt_nums is not None and self.gt_nums.find("|") >= 0

    def __getitem__(self, key):
        """ Lookup value, backwards compatibility """
        return self.data[key]

    @property
    def is_variant(self):
        """ Return True if not a reference call """
        if not self.called:
            return None
        return self.gt_type != 0

    @property
    def is_het(self):
        """ Return True for heterozygous calls """
        if not self.called:
            return None
        return self.gt_type == 1


class _Record(object):
    """ A set of calls at a site.  Equivalent to a row in a VCF file.

        The standard VCF fields CHROM, POS, ID, REF, ALT, QUAL, FILTER,
        INFO and FORMAT are available as properties.

        The list of genotype calls is in the ``samples`` property.
    """
    def __init__(self, CHROM, POS, ID, REF, ALT, QUAL, FILTER, INFO, FORMAT,
            sample_indexes, samples=None):
        self.CHROM = CHROM
        self.POS = POS
        self.ID = ID
        self.REF = REF
        self.ALT = ALT
        self.QUAL = QUAL
        self.FILTER = FILTER
        self.INFO = INFO
        self.FORMAT = FORMAT
        #: 0-based start coordinate
        self.start = self.POS - 1
        #: 1-based end coordinate
        self.end = self.start + len(self.REF)
        #: list of alleles. [0] = REF, [1:] = ALTS
        self.alleles = [self.REF]
        self.alleles.extend(self.ALT)
        #: list of ``_Calls`` for each sample ordered as in source VCF
        self.samples = samples
        self._sample_indexes = sample_indexes

    def __eq__(self, other):
        """ _Records are equal if they describe the same variant (same position, alleles) """
        return (self.CHROM == other.CHROM and
                self.POS == other.POS and
                self.REF == other.REF and
                self.ALT == other.ALT)

    def __iter__(self):
        return iter(self.samples)

    def __str__(self):
        return "Record(CHROM=%(CHROM)s, POS=%(POS)s, REF=%(REF)s, ALT=%(ALT)s)" % self.__dict__

    def __cmp__(self, other):
        return cmp( (self.CHROM, self.POS), (other.CHROM, other.POS))

    def add_format(self, fmt):
        self.FORMAT = self.FORMAT + ':' + fmt

    def add_filter(self, flt):
        if self.FILTER is None \
        or self.FILTER == 'PASS'\
        or self.FILTER == '.':
            self.FILTER = ''
        else:
            self.FILTER = self.FILTER + ';'
        self.FILTER = self.FILTER + flt

    def add_info(self, info, value=True):
        self.INFO[info] = value

    def genotype(self, name):
        """ Lookup a ``_Call`` for the sample given in ``name`` """
        return self.samples[self._sample_indexes[name]]

    @property
    def num_called(self):
        """ The number of called samples"""
        return sum(s.called for s in self.samples)

    @property
    def call_rate(self):
        """ The fraction of genotypes that were actually called. """
        return float(self.num_called) / float(len(self.samples))

    @property
    def num_hom_ref(self):
        """ The number of homozygous for ref allele genotypes"""
        return len([s for s in self.samples if s.gt_type == 0])

    @property
    def num_hom_alt(self):
        """ The number of homozygous for alt allele genotypes"""
        return len([s for s in self.samples if s.gt_type == 2])

    @property
    def num_het(self):
        """ The number of heterozygous genotypes"""
        return len([s for s in self.samples if s.gt_type == 1])

    @property
    def num_unknown(self):
        """ The number of unknown genotypes"""
        return len([s for s in self.samples if s.gt_type is None])

    @property
    def aaf(self):
        """ The allele frequency of the alternate allele.
           NOTE 1: Punt if more than one alternate allele.
           NOTE 2: Denominator calc'ed from _called_ genotypes.
        """
        # skip if more than one alternate allele. assumes bi-allelic
        if len(self.ALT) > 1:
            return None
        hom_ref = self.num_hom_ref
        het = self.num_het
        hom_alt = self.num_hom_alt
        num_chroms = float(2.0 * self.num_called)
        return float(het + 2 * hom_alt) / float(num_chroms)

    @property
    def nucl_diversity(self):
        """
        pi_hat (estimation of nucleotide diversity) for the site.
        This metric can be summed across multiple sites to compute regional
        nucleotide diversity estimates.  For example, pi_hat for all variants
        in a given gene.

        Derived from:
        \"Population Genetics: A Concise Guide, 2nd ed., p.45\"
          John Gillespie.
        """
        # skip if more than one alternate allele. assumes bi-allelic
        if len(self.ALT) > 1:
            return None
        p = self.aaf
        q = 1.0 - p
        num_chroms = float(2.0 * self.num_called)
        return float(num_chroms / (num_chroms - 1.0)) * (2.0 * p * q)

    def get_hom_refs(self):
        """ The list of hom ref genotypes"""
        return [s for s in self.samples if s.gt_type == 0]

    def get_hom_alts(self):
        """ The list of hom alt genotypes"""
        return [s for s in self.samples if s.gt_type == 2]

    def get_hets(self):
        """ The list of het genotypes"""
        return [s for s in self.samples if s.gt_type == 1]

    def get_unknowns(self):
        """ The list of unknown genotypes"""
        return [s for s in self.samples if s.gt_type is None]

    @property
    def is_snp(self):
        """ Return whether or not the variant is a SNP """
        if len(self.REF) > 1: return False
        for alt in self.ALT:
            if alt is None or alt.type != "SNV":
                return False
            if alt not in ['A', 'C', 'G', 'T']:
                return False
        return True

    @property
    def is_indel(self):
        """ Return whether or not the variant is an INDEL """
        is_sv = self.is_sv

        if len(self.REF) > 1 and not is_sv: return True
        for alt in self.ALT:
            if alt is None:
                return True
            if alt.type != "SNV" and alt.type != "MNV":
                return False
            elif len(alt) != len(self.REF):
                # the diff. b/w INDELs and SVs can be murky.
                if not is_sv:
                    # 1	2827693	.	CCCCTCGCA	C	.	PASS	AC=10;
                    return True
                else:
                    # 1	2827693	.	CCCCTCGCA	C	.	PASS	SVTYPE=DEL;
                    return False
        return False

    @property
    def is_sv(self):
        """ Return whether or not the variant is a structural variant """
        if self.INFO.get('SVTYPE') is None:
            return False
        return True

    @property
    def is_transition(self):
        """ Return whether or not the SNP is a transition """
        # if multiple alts, it is unclear if we have a transition
        if len(self.ALT) > 1: return False

        if self.is_snp:
            # just one alt allele
            alt_allele = self.ALT[0]
            if ((self.REF == "A" and alt_allele == "G") or
                (self.REF == "G" and alt_allele == "A") or
                (self.REF == "C" and alt_allele == "T") or
                (self.REF == "T" and alt_allele == "C")):
                return True
            else: return False
        else: return False

    @property
    def is_deletion(self):
        """ Return whether or not the INDEL is a deletion """
        # if multiple alts, it is unclear if we have a transition
        if len(self.ALT) > 1: return False

        if self.is_indel:
            # just one alt allele
            alt_allele = self.ALT[0]
            if alt_allele is None:
                return True
            if len(self.REF) > len(alt_allele):
                return True
            else: return False
        else: return False

    @property
    def var_type(self):
        """
        Return the type of variant [snp, indel, unknown]
        TO DO: support SVs
        """
        if self.is_snp:
            return "snp"
        elif self.is_indel:
            return "indel"
        elif self.is_sv:
            return "sv"
        else:
            return "unknown"

    @property
    def var_subtype(self):
        """
        Return the subtype of variant.
        - For SNPs and INDELs, yeild one of: [ts, tv, ins, del]
        - For SVs yield either "complex" or the SV type defined
          in the ALT fields (removing the brackets).
          E.g.:
               <DEL>       -> DEL
               <INS:ME:L1> -> INS:ME:L1
               <DUP>       -> DUP

        The logic is meant to follow the rules outlined in the following
        paragraph at:

        http://www.1000genomes.org/wiki/Analysis/Variant%20Call%20Format/vcf-variant-call-format-version-41

        "For precisely known variants, the REF and ALT fields should contain
        the full sequences for the alleles, following the usual VCF conventions.
        For imprecise variants, the REF field may contain a single base and the
        ALT fields should contain symbolic alleles (e.g. <ID>), described in more
        detail below. Imprecise variants should also be marked by the presence
        of an IMPRECISE flag in the INFO field."
        """
        if self.is_snp:
            if self.is_transition:
                return "ts"
            elif len(self.ALT) == 1:
                return "tv"
            else: # multiple ALT alleles.  unclear
                return "unknown"
        elif self.is_indel:
            if self.is_deletion:
                return "del"
            elif len(self.ALT) == 1:
                return "ins"
            else: # multiple ALT alleles.  unclear
                return "unknown"
        elif self.is_sv:
            if self.INFO['SVTYPE'] == "BND":
                return "complex"
            elif self.is_sv_precise:
                return self.INFO['SVTYPE']
            else:
                return self.ALT[0].type
        else:
            return "unknown"

    @property
    def sv_end(self):
        """ Return the end position for the SV """
        if self.is_sv:
            return self.INFO['END']
        return None

    @property
    def is_sv_precise(self):
        """ Return whether the SV cordinates are mapped
            to 1 b.p. resolution.
        """
        if self.INFO.get('IMPRECISE') is None and not self.is_sv:
            return False
        elif self.INFO.get('IMPRECISE') is not None and self.is_sv:
            return False
        elif self.INFO.get('IMPRECISE') is None and self.is_sv:
            return True

    @property
    def is_monomorphic(self):
        """ Return True for reference calls """
        return len(self.ALT) == 1 and self.ALT[0] is None


class Reader(object):
    """ Reader for a VCF v 4.0 file, an iterator returning ``_Record objects`` """


    def __init__(self, fsock=None, filename=None, compressed=False, prepend_chr=False):
        """ Create a new Reader for a VCF file.

            You must specify either fsock (stream) or filename.  Gzipped streams
            or files are attempted to be recogized by the file extension, or gzipped
            can be forced with ``compressed=True``
        """
        super(VCFReader, self).__init__()

        if not (fsock or filename):
            raise Exception('You must provide at least fsock or filename')

        if fsock:
            self.reader = fsock
            if filename is None and hasattr(fsock, 'name'):
                filename = fsock.name
                compressed = compressed or filename.endswith('.gz')
        elif filename:
            compressed = compressed or filename.endswith('.gz')
            self.reader = open(filename, 'rb' if compressed else 'rt')
        self.filename = filename
        if compressed:
            self.reader = gzip.GzipFile(fileobj=self.reader)
            if sys.version > '3':
                self.reader = codecs.getreader('ascii')(self.reader)

        #: metadata fields from header (string or hash, depending)
        self.metadata = None
        #: INFO fields from header
        self.infos = None
        #: FILTER fields from header
        self.filters = None
        #: ALT fields from header
        self.alts = None
        #: FORMAT fields from header
        self.formats = None
        self.samples = None
        self._sample_indexes = None
        self._header_lines = []
        self._tabix = None
        self._prepend_chr = prepend_chr
        self._parse_metainfo()
        self._format_cache = {}

    def __iter__(self):
        return self

    def _parse_metainfo(self):
        '''Parse the information stored in the metainfo of the VCF.

        The end user shouldn't have to use this.  She can access the metainfo
        directly with ``self.metadata``.'''
        for attr in ('metadata', 'infos', 'filters', 'alts', 'formats'):
            setattr(self, attr, OrderedDict())

        parser = _vcf_metadata_parser()

        line = self.reader.next()
        while line.startswith('##'):
            self._header_lines.append(line)
            line = line.strip()

            if line.startswith('##INFO'):
                key, val = parser.read_info(line)
                self.infos[key] = val

            elif line.startswith('##FILTER'):
                key, val = parser.read_filter(line)
                self.filters[key] = val

            elif line.startswith('##ALT'):
                key, val = parser.read_alt(line)
                self.alts[key] = val

            elif line.startswith('##FORMAT'):
                key, val = parser.read_format(line)
                self.formats[key] = val

            else:
                key, val = parser.read_meta(line.strip())
                if key in SINGULAR_METADATA:
                    self.metadata[key] = val
                else:
                    if key not in self.metadata:
                        self.metadata[key] = []
                    self.metadata[key].append(val)

            line = self.reader.next()

        fields = re.split('\t| +', line.rstrip())
        self.samples = fields[9:]
        self._sample_indexes = dict([(x,i) for (i,x) in enumerate(self.samples)])

    def _map(self, func, iterable, bad='.'):
        '''``map``, but make bad values None.'''
        return [func(x) if x != bad else None
                for x in iterable]

    def _parse_info(self, info_str):
        '''Parse the INFO field of a VCF entry into a dictionary of Python
        types.

        '''
        if info_str == '.':
            return {}

        entries = info_str.split(';')
        retdict = OrderedDict()

        for entry in entries:
            entry = entry.split('=')
            ID = entry[0]
            try:
                entry_type = self.infos[ID].type
            except KeyError:
                try:
                    entry_type = RESERVED_INFO[ID]
                except KeyError:
                    if entry[1:]:
                        entry_type = 'String'
                    else:
                        entry_type = 'Flag'

            if entry_type == 'Integer':
                vals = entry[1].split(',')
                val = self._map(int, vals)
            elif entry_type == 'Float':
                vals = entry[1].split(',')
                val = self._map(float, vals)
            elif entry_type == 'Flag':
                val = True
            elif entry_type == 'String':
                try:
                    val = entry[1]
                except IndexError:
                    val = True

            try:
                if self.infos[ID].num == 1 and entry_type != 'String':
                    val = val[0]
            except KeyError:
                pass

            retdict[ID] = val

        return retdict

    def _parse_sample_format(self, samp_fmt):
        """ Parse the format of the calls in this _Record """
        samp_fmt = samp_fmt.split(':')

        samp_fmt_types = []
        samp_fmt_nums = []

        for fmt in samp_fmt:
            try:
                entry_type = self.formats[fmt].type
                entry_num = self.formats[fmt].num
            except KeyError:
                entry_num = None
                try:
                    entry_type = RESERVED_FORMAT[fmt]
                except KeyError:
                    entry_type = 'String'
            samp_fmt_types.append(entry_type)
            samp_fmt_nums.append(entry_num)
        return samp_fmt, samp_fmt_types, samp_fmt_nums

    def _parse_samples(self, samples, samp_fmt, site):
        '''Parse a sample entry according to the format specified in the FORMAT
        column.'''

        # check whether we already know how to parse this format
        if samp_fmt in self._format_cache:
            samp_fmt, samp_fmt_types, samp_fmt_nums = \
                    self._format_cache[samp_fmt]
        else:
            sf, samp_fmt_types, samp_fmt_nums = self._parse_sample_format(samp_fmt)
            self._format_cache[samp_fmt] = (sf, samp_fmt_types, samp_fmt_nums)
            samp_fmt = sf

        samp_data = []
        _map = self._map

        for name, sample in itertools.izip(self.samples, samples):

            # parse the data for this sample
            sampdict = dict([(x, None) for x in samp_fmt])

            for fmt, entry_type, entry_num, vals in itertools.izip(
                    samp_fmt, samp_fmt_types, samp_fmt_nums, sample.split(':')):

                # short circuit the most common
                if vals == '.' or vals == './.':
                    sampdict[fmt] = None
                    continue

                # we don't need to split single entries
                if entry_num == 1 or ',' not in vals:

                    if entry_type == 'Integer':
                        sampdict[fmt] = int(vals)
                    elif entry_type == 'Float':
                        sampdict[fmt] = float(vals)
                    else:
                        sampdict[fmt] = vals

                    if entry_num != 1:
                        sampdict[fmt] = (sampdict[fmt])

                    continue

                vals = vals.split(',')

                if entry_type == 'Integer':
                    sampdict[fmt] = _map(int, vals)
                elif entry_type == 'Float' or entry_type == 'Numeric':
                    sampdict[fmt] = _map(float, vals)
                else:
                    sampdict[fmt] = vals

            # create a call object
            call = _Call(site, name, sampdict)
            samp_data.append(call)

        return samp_data

    def parseALT(self, str):
        if re.search('[\[\]]', str) is not None:
            # Paired breakend
            items = re.split('[\[\]]', str)
            remoteCoords = items[1].split(':')
            chr = remoteCoords[0]
            if chr[0] == '<':
                chr = chr[1:-1]
                withinMainAssembly = False
            else:
                withinMainAssembly = True
            pos = remoteCoords[1]
            orientation = (str[0] == '[' or str[0] == ']')
            remoteOrientation = (re.search('\[', str) is not None)
            if orientation:
                connectingSequence = items[2]
            else:
                connectingSequence = items[0]
            return _Breakend(chr, pos, orientation, remoteOrientation, connectingSequence, withinMainAssembly)
        elif str[0] == '.' and len(str) > 1:
            return _SingleBreakend(True, str[1:])
        elif str[-1] == '.' and len(str) > 1:
            return _SingleBreakend(False, str[:-1])
        elif str[0] == "<" and str[-1] == ">":
            return _SV(str[1:-1])
        else:
            return _Substitution(str)

    def next(self):
        '''Return the next record in the file.'''
        line = self.reader.next()
        row = re.split('\t| +', line.strip())
        chrom = row[0]
        if self._prepend_chr:
            chrom = 'chr' + chrom
        pos = int(row[1])

        if row[2] != '.':
            ID = row[2]
        else:
            ID = None

        ref = row[3]
        alt = self._map(self.parseALT, row[4].split(','))

        try:
            qual = int(row[5])
        except ValueError:
            try:
                qual = float(row[5])
            except ValueError:
                qual = None

        filt = row[6].split(';') if ';' in row[6] else row[6]
        if filt == 'PASS':
            filt = None
        info = self._parse_info(row[7])

        try:
            fmt = row[8]
        except IndexError:
            fmt = None

        record = _Record(chrom, pos, ID, ref, alt, qual, filt,
                info, fmt, self._sample_indexes)

        if fmt is not None:
            samples = self._parse_samples(row[9:], fmt, record)
            record.samples = samples

        return record

    def fetch(self, chrom, start, end=None):
        """ fetch records from a Tabix indexed VCF, requires pysam
            if start and end are specified, return iterator over positions
            if end not specified, return individual ``_Call`` at start or None
        """
        if not pysam:
            raise Exception('pysam not available, try "pip install pysam"?')

        if not self.filename:
            raise Exception('Please provide a filename (or a "normal" fsock)')

        if not self._tabix:
            self._tabix = pysam.Tabixfile(self.filename)

        if self._prepend_chr and chrom[:3] == 'chr':
            chrom = chrom[3:]

        # not sure why tabix needs position -1
        start = start - 1

        if end is None:
            self.reader = self._tabix.fetch(chrom, start, start + 1)
            try:
                return self.next()
            except StopIteration:
                return None

        self.reader = self._tabix.fetch(chrom, start, end)
        return self


class Writer(object):
    """ VCF Writer """

    fixed_fields = "#CHROM POS ID REF ALT QUAL FILTER INFO FORMAT".split()

    # Reverse keys and values in header field count dictionary
    counts = dict((v,k) for k,v in field_counts.iteritems())

    def __init__(self, stream, template, lineterminator="\r\n"):
        self.writer = csv.writer(stream, delimiter="\t", lineterminator=lineterminator)
        self.template = template

        two = '##{key}=<ID={0},Description="{1}">\n'
        four = '##{key}=<ID={0},Number={num},Type={2},Description="{3}">\n'
        _num = self._fix_field_count
        for (key, vals) in template.metadata.iteritems():
            if key in SINGULAR_METADATA:
                vals = [vals]
            for val in vals:
                stream.write('##{0}={1}\n'.format(key, val))
        for line in template.infos.itervalues():
            stream.write(four.format(key="INFO", *line, num=_num(line.num)))
        for line in template.formats.itervalues():
            stream.write(four.format(key="FORMAT", *line, num=_num(line.num)))
        for line in template.filters.itervalues():
            stream.write(two.format(key="FILTER", *line))
        for line in template.alts.itervalues():
            stream.write(two.format(key="ALT", *line))

        self._write_header()

    def _write_header(self):
        # TODO: write INFO, etc
        self.writer.writerow(self.fixed_fields + self.template.samples)

    def write_record(self, record):
        """ write a record to the file """
        ffs = self._map(str, [record.CHROM, record.POS, record.ID, record.REF]) \
              + [self._format_alt(record.ALT), record.QUAL or '.', self._format_filter(record.FILTER),
                 self._format_info(record.INFO), record.FORMAT]

        samples = [self._format_sample(record.FORMAT, sample)
            for sample in record.samples]
        self.writer.writerow(ffs + samples)

    def _fix_field_count(self, num_str):
        """Restore header number to original state"""
        if num_str not in self.counts:
            return num_str
        else:
            return self.counts[num_str]

    def _format_alt(self, alt):
        return ','.join(self._map(str, alt))

    def _format_filter(self, flt):
        return self._stringify(flt, none='PASS', delim=';')

    def _format_info(self, info):
        if not info:
            return '.'
        return ';'.join([self._stringify_pair(x,y) for x, y in info.iteritems()])

    def _format_sample(self, fmt, sample):
        if sample.data["GT"] is None:
            return "./."
        return ':'.join(self._stringify(sample.data[f]) for f in fmt.split(':'))

    def _stringify(self, x, none='.', delim=','):
        if type(x) == type([]):
            return delim.join(self._map(str, x, none))
        return str(x) if x is not None else none

    def _stringify_pair(self, x, y, none='.', delim=','):
        if y and isinstance(y, bool):
            return str(x)
        return "%s=%s" % (str(x), self._stringify(y, none=none, delim=delim))

    def _map(self, func, iterable, none='.'):
        '''``map``, but make None values none.'''
        return [func(x) if x is not None else none
                for x in iterable]


def __update_readme():
    import sys, vcf
    file('README.rst', 'w').write(vcf.__doc__)


# backwards compatibility
VCFReader = Reader
VCFWriter = Writer
