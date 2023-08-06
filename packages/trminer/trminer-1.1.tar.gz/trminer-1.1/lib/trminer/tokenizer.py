import index
import re
from tokens import NoTokenException

class Tokenizer:
	"""
	Tokenization of a given text file.
	"""
	
	def __init__(self, tokens):
		"""
		Arguments:
		tokens -- a Tokens object
		"""
		
		self.__tokens = tokens
	
	def tokenize(self, filepath, tokenizedfilepath, indexfilepath, lastindexfilepath, tokenlengthindexfilepath):
		"""
		Tokenize a given text file.
		
		Arguments:
		filepath -- the text file
		tokenizedfilepath -- the tokenized file
		indexfilepath -- the file containing the index positions of each token
		lastindexfilepath -- the file containing for each token the last index position of a token with the same inverse image
		"""
		
		file = open(filepath).read()
		tokenizedfile = open(tokenizedfilepath, "w")
		indexwriter = index.IndexWriter(indexfilepath)
		lastindexwriter = index.IndexWriter(lastindexfilepath)
		tokenlengthindexwriter = index.IndexWriter(tokenlengthindexfilepath)
		
		splitter = Wordsplitter()
		
		tokens = set()
		tokenized = ""
		
		lastindex = dict()
		words = splitter.split(file)
		i = 0
		while i < len(words):
			try:
				token, next = self.__tokens.token(words, i)
				word = " ".join(words[i:next])
				
				tokenized += token
				tokens.add(token)
				
				indexwriter.write(i)
				lastindexwriter.write(lastindex.get(word, -1))
				tokenlengthindexwriter.write(next-i)
				
				lastindex[word] = i
				i = next
			except NoTokenException:
				i += 1
		
		tokenizedfile.write("".join(tokens) + "\n")
		tokenizedfile.write(tokenized)
		
		tokenizedfile.close()
		indexwriter.close()

def read_tokens(tokenizedfilepath):
	return frozenset(open(tokenizedfilepath).next().rstrip())

def read_tokenized(tokenizedfilepath):
	"""
	Return a tokenized file as a string.
	
	Arguments:
	tokenizedfilepath -- the tokenized file 
	"""
	
	tokenizedfile = open(tokenizedfilepath)
	tokenizedfile.next()
	return tokenizedfile.next().rstrip()

class Wordsplitter:
	"""
	Splits a given text into a sequence of words.
	"""
	
	def __init__(self):
		self.__splitter = re.compile("\s") #re.compile("[^\.\?\!\w-]")
		self.__fullstop = re.compile("[\.\?\!]\s")
		self.__slash = re.compile("/")
		
	def split(self, text):
		"""
		Returns a sequence of words from a given text.
		
		Arguments:
		text -- the text
		"""
		return self.__splitter.split(self.__fullstop.sub(" . ", self.__slash.sub("/ ", text)))
	
	def get_word_end(self, text):
		return self.__splitter.search(text).start()