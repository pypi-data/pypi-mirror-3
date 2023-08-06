class Tokens:
	"""
	Management of given tokens.
	"""
	
	def __init__(self, tokenfilepath):
		"""
		Arguments:
		tokenfilepath -- path to the file defining tokens and their inverse image
		"""
		
		self.__tokentree = TokenTree()
		self.__words = dict()
		for l in open(tokenfilepath):
			if not l.startswith("#") and len(l) > 1:
				l = l.rstrip().split("\t")
				token = l[0].lower()
				if len(token) > 1:
					raise IOError("Token identifier has to be a single character.")
				self.__words[token] = []
				for w in l[1:]:
					w = w.lower()
					self.__words[token].append(w)
					self.__tokentree.add_token(w, token)
		for fullstop in (".?!"):
			self.__tokentree.add_token(fullstop, ".")
		
	def __iter__(self):
		"""
		Iterate over the tokens.
		"""
		
		return self.__words.__iter__()
	
	def words(self, token):
		"""
		Return words for a given token.
		"""
		
		return self.__words[token]
	
	def token(self, words, i):
		"""
		Return token for a given position i in a sequence of words.
		
		Arguments:
		words -- the sequence of words as a list
		i -- the position in the sequence
		"""
		
		return self.__tokentree.get_token(words, i)


class TokenTree:
	"""
	Store tokens in a dictionary tree of words.
	"""
	
	def __init__(self):
		self.__root = TokenTreeNode()
	
	def add_token(self, word, token):
		"""
		Add a token to the tree.
		
		Arguments:
		word -- the word that is the inverse image of the token. May contain whitespaces.
		token -- the token
		"""
		
		word = word.split()
		node = self.__root
		for w in word:
			if not w in node.children:
				node.children[w] = TokenTreeNode()
			node = node.children[w]
		node.token = token
	
	def get_token(self, words, i):
		"""
		Returns the token for a given position i in a sequence of words.
		
		Arguments:
		words -- the sequence of words as a list
		i -- the position in the sequence of words
		"""
		
		word = self.normalize_word(words[i])
		candidates = []
		node = self.__root
		while word in node.children:
			n = node.children[word]
			if n.token:
				candidates.append((n.token, i+1))
			i += 1
			word = self.normalize_word(words[i])
			node = n
		if len(candidates) > 0:
			return candidates[-1] # return the longest possible match
		raise NoTokenException()
	
	def normalize_word(self, word):
		if word == ".": return word
		return word.lower().strip(",.!?:;/()[]{}")

class TokenTreeNode:
	"""
	A node in the dictionary tree for tokens.
	"""
	
	def __init__(self):
		self.children = dict()
		self.token = None

class NoTokenException(Exception):
    pass
