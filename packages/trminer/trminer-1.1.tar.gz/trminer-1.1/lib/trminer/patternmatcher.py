import tokenizer
import index

class PatternMatcher:
	"""
	Pattern matching.
	"""
	
	def __init__(self, patterns, tokens):
		"""
		Arguments:
		patterns -- the Patterns object
		tokens -- the Tokens object
		"""
		
		self.__patterns = patterns
		self.__tokens = tokens
		
	def match(self, originalfilepath, tokenizedfilepath, indexfilepath, lastindexfilepath, tokenlengthindexfilepath):
		"""
		Match patterns in a given file.
		
		Arguments:
		originalfilepath -- the text file
		tokenizedfilepath -- the tokenized file
		indexfilepath -- the file containing the index positions of each token
		lastindexfilepath -- the file containing for each token the last index position of a token with the same inverse image
		"""
		
		# abort if required tokens are not even found in this paper
		if not self.__patterns.has_pattern_with_tokens(tokenizer.read_tokens(tokenizedfilepath)):
			return
		
		tokenized = tokenizer.read_tokenized(tokenizedfilepath)
		index_reader = index.IndexReader(indexfilepath)
		lastindex_reader = index.IndexReader(lastindexfilepath)
		tokenlengthindex_reader = index.IndexReader(tokenlengthindexfilepath)
		
		originalfile = open(originalfilepath).read()
		originalfile = tokenizer.Wordsplitter().split(originalfile)
		
		for match in self.__patterns.finditer(tokenized):
			# ensure that tokens marked as unique appear only once in their real form match
			if self.__violates_unique(match, tokenized, index_reader, lastindex_reader):
				continue
			
			s = match.start()
			while s > 0 and tokenized[s] != "." :
				s -= 1
			
			e = match.end()
			
			while e < len(tokenized) and tokenized[e-1] != "." :
				e += 1
			
			start = index_reader.get(s)
			end = index_reader.get(e-1)
			
			text = originalfile[start:end+1]
			
			to_mark = [(index_reader.get(i) - start, tokenlengthindex_reader.get(i)) for i in range(s+1, e-1)]
			
			yield text, self.__patterns.get_pattern(match.lastgroup), to_mark
	
	def __violates_unique(self, match, tokenized, index_reader, lastindex_reader):
		"""
		Returns true if a given match contains several identical inverse images of a token marked as unique for the pattern.
		
		Arguments:
		match -- the match object
		tokenized -- the sequence of tokens from the tokenized file
		index_reader -- the index reader object
		lastindex_reader -- the lastindex reader object.
		"""
		
		pattern = match.lastgroup
		unique = self.__patterns.get_unique(pattern)
		
		start = index_reader.get(match.start())
		for i in range(match.start(), match.end()):
			if tokenized[i] in unique:
				if lastindex_reader.get(i) >= start:
					return True
		return False