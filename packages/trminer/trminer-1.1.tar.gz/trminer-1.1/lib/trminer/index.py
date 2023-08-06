class IndexWriter:
	"""
	Write a token index to a file.
	"""
	
	def __init__(self, indexfilepath):
		"""
		Arguments:
		indexfilepath -- the index file
		"""
		
		self.__file = open(indexfilepath, "w")
	
	def write(self, index):
		"""
		Write an index into the file.
		"""
		
		self.__file.write(str(index) + " ")
		
	def close(self):
		"""
		Close the file.
		"""
		
		self.__file.close()
		
class IndexReader:
	"""
	Read a token index file.
	"""
	
	def __init__(self, indexfilepath):
		"""
		Arguments:
		indexfilepath -- the index file
		"""
		
		self.__index = [int(i) for i in open(indexfilepath).next().rstrip().split()]
		
	def get(self, column):
		"""
		Returns the index at given column.
		"""
		
		if column < 0 or column >= len(self.__index):
			print column
			return None
		return self.__index[column]