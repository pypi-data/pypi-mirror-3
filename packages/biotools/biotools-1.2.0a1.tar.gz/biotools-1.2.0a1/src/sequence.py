from biotools.annotation import Annotation

def chop(seq,length = 70):
	'''chop( sequence, length = 70 )
Yields a chunk of a sequence of no more than length characters,
it is meant to be used to print fasta files.'''

	while seq:
		try: piece, seq = seq[:length], seq[length:]
		except: piece, seq = seq, ''
		yield piece
	raise StopIteration


class Sequence(object):
	'''class Sequence
A wrapper class for sequences.'''

	def __init__(self, name, seq, **kwargs):
		'''Sequence( name, sequence, ... )
Instantiates a Sequence object with a given sequence. Some other useful
parameters that the Sequence constructor can handle are:
	* qual				=> the quality scores (an array of integers) of the sequence,
	* type				=> the type of the sequence, either prot or nucl,
	* start			 => the starting position of the sequence within a supersequence,
	* end				 => the ending position of the sequnece within a supersequence,
	* step				=> the 'step' of the sequence, usually +1 for top-strand 
									 sequences, and -1 for bottom-strand sequences, but can handle 
									 other values as well,
	* original		=> the original Sequence object from which this one derives,
	* defline		 => the definition line for this sequnce from a fasta file.
If one of these are not given, they will default to the most logical value
that can be determined from the other values and sequence (e.g., 
if end < start, then step is probably -1).'''

		self.name = name
		self.seq = seq.upper()
		self.qual = kwargs.get('qual',None)
		self.type = kwargs.get('type','prot' if set(seq)-set('ATUCGNYR') \
			else 'nucl')
		self.start = kwargs.get('start',1)
		self.end = kwargs.get('end',len(seq))
		self.step = kwargs.get('step', -1 if self.start > self.end else 1)
		self.original = kwargs.get('original',self)
		self.defline = kwargs.get('defline','')

	def __getitem__(self,key):
		'''sequence[i] or sequence[start:end] or sequence[start:end:step] constructs a new Sequence that is a subsequence as described by the way this function is called. This function will automatically fill in the name, sequence, start, stop, step, original, and type of the subsequence. It also tries to fill in the annotations, but annotations are handled pretty poorly right now, so it's probably best not to worry about those, but it will work if you really want to.'''

		try:
			start, stop, step = key.indices(len(self.seq))
		except AttributeError: start, stop, step = key, key+1, 1

		seq = ''.join(self.seq[x] for x in xrange(start,stop,step))
		qual = self.qual and [self.qual[x] for x in xrange(start,stop,step)]

		order = 1 if step >= 0 else -1
		sorder = 1 if self.step > 0 else -1
		dstart, dend = (self.step * start, self.step * (stop-1))[::order]
		pstart, pend = (self.start, self.end)[::sorder]
		newstart, newend = pstart + dstart, pstart + dend

		info = (self.name, start, stop, step)
		return Sequence("subsequence(%s,%d,%d,%d)" % info, seq, 
			qual=qual, original=self.original, type=self.type,
			start=newstart, end=newend, step=step * self.step)

	'''Some other things you can do with a Sequence object:
* len(sequence)		=> gives the length of the sequence.
* sequence.upper() => technically does nothing, but returns the sequence with a capitalized version of the sequence (which is done on instantiation, now).
* for character in sequence: => allows you to loop over each character in the sequence.
* dictionary[sequence] => allows sequences to be used as keys for dictionaries and allows you to have sequences in sets. This relies on the test seqA == seqB, described next.
* seqA == seqB		 => compare two sequences. The sequences are the same if they have the same sequence AND name. Therefore, two sequences with different names are treated as separate items in a set and separate keys in a dictionary. If you need to match only the sequence, use seqA.seq == seqB.seq.
* print sequence	 => print a fasta / fastq (depending on whether there are any quality scores) representation of the sequence. Sequence objects in any other data structure (e.g., list, dictionary) are printed as (e.g., <Sequence 0x000000>). If you want to change that, you can do:
	def __repr__(self): return self.__str__()'''

	def __len__(self):
		return len(self.seq)
		
	def upper(self):
		return self
	
	def __iter__(self):
		for i in xrange(len(self)):
			yield self.seq[i:i+1]
		raise StopIteration
		
	def __hash__(self):	
		return self.seq.__hash__();
		
	def __eq__(self,other):
		try:
			return self.seq == other.seq and self.name == other.name
		except AttributeError:
			return (self.seq == other)
			
	def __str__(self):
		if self.qual:
			return '@%s\n%s\n+\n%s' % (self.name, self.seq, 
				''.join(chr(ord('A') - 1 + q) for q in self.qual))
		else:
			return '>%s %s\n%s' % (self.name, self.defline, 
				'\n'.join(chop(self.seq, 70)))

	def __contains__(self, sub):
		return sub in self.seq


def annotation(seq, source, type, **kwargs):
	'''annotation(sequence, source, type, **kwargs)
Creates an Annotation object for the given sequence from a source (e.g., "phytozome7.0") of a particular type (e.g., "gene").'''
	try: sname = source.name
	except AttributeError: sname = source
	
	start, end = min(seq.start, seq.end), max(seq.start, seq.end)
	strand = '+' if seq.step == 1 else '-'
	attrs = ';'.join('%s=%s' % (key, str(kwargs[key])) for key in kwargs)
	
	return Annotation(seq.original.name, sname, type, start, end, '.',
		strand, start % 3, attrs)
