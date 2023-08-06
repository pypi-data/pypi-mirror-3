import re

class Patterns:
	"""
	Management of patterns.
	"""
	
	def __init__(self, patternfilepath, tokens):
		"""
		Arguments:
		patternfilepath -- the file containing pattern definitions
		tokens -- the Tokens object
		"""
		
		self.__tokens = []
		self.__patterns = []
		self.__unique = []
		for l in open(patternfilepath):
			if not l.startswith("#") and len(l) > 1:
				l = l.rstrip().split("\t")
				p = l[0]
				u = l[1] if len(l) > 1 else ""
				self.__patterns.append(p)
				self.__unique.append(u)
				self.__tokens.append(frozenset(re.sub(r'\W+', '', p)))
		
		self.disjunction = "(?P<pattern0>" + self.__patterns[0] + ")"
		for i in range(1,len(self.__patterns)):
			self.disjunction += "|(?P<pattern" + str(i) + ">" + self.__patterns[i] + ")"
			
		self.disjunction = re.compile(self.disjunction)
	
	def __iter__(self):
		"""
		Iterator over managed patterns.
		"""
		
		return self.__patterns.__iter__()
	
	def get_pattern(self, i):
		"""
		Returns the ith pattern.
		"""
		
		return self.__patterns[int(i[7:])]
	
	def get_unique(self, i):
		"""
		Returns true if the ith pattern is unique.		
		"""
		
		return self.__unique[int(i[7:])]
	
	def has_pattern_with_tokens(self, tokens):
		for t in self.__tokens:
			if t <= tokens: return True
		return False
	
	def finditer(self, tokenizedtext):
		"""
		Iteratively find occurences of any managed pattern in a given tokenized text.
		
		Arguments:
		tokenizedtext -- the tokenized text
		"""
		
		return re.finditer(self.disjunction, tokenizedtext)
