# -*- coding: utf-8 -*-

import re
from jinja2 import Template
import os
from tokenizer import Wordsplitter

class HTMLOutput:
	"""
	Output the match results into an HTML document.
	"""
	
	def __init__(self, outputfilepath, tokens, patterns):
		"""
		Arguments:
		outputfilepath -- the path to the output HTML file
		tokens -- the Tokens object
		patterns -- the Patterns object
		"""
		
		self.__outputfilepath = outputfilepath
		self.__papers = []
		self.__tokens = tokens
		self.__patterns = patterns
	
	def add_paper(self, title, filepath, filename):
		"""
		Add a paper to the output.
		
		Arguments:
		title -- the title of the paper table
		filepath -- the path to the original file
		filename -- the file name
		"""
		
		paper = Paper(title, filepath, filename)
		self.__papers.append(paper)
		return paper
	
	def write(self):
		"""
		Write output to file and close file.
		"""
		
		patterns = dict()
		for paper in self.__papers:
			for m in paper.matches:
				if not m.pattern in patterns:
					patterns[m.pattern] = 0
				patterns[m.pattern] += 1
		for pattern in self.__patterns:
			if not pattern in patterns:
				patterns[pattern] = 0
		
		htmlfile = open(self.__outputfilepath, "w")
		#tmpl = MarkupTemplate(open(os.path.join(os.path.dirname(__file__),'output.html')))
		#stream = tmpl.generate(papers = self.__papers, patterns = patterns, tokens = self.__tokens)
		template = Template(open(os.path.join(os.path.dirname(__file__),'output.html')).read())
		
		html = template.render(papers = self.__papers, patterns = patterns, tokens = self.__tokens, allpatterns = sum(patterns.values()), numpapers = len(self.__papers)
			).encode("utf-8")
		htmlfile.write(html)
		htmlfile.close()

class Paper:
	"""
	Container for information and matches of a paper.
	"""
	
	def __init__(self, title, filepath, filename):
		"""
		Arguments:
		title -- the title of the table entry
		filepath -- the original file containing the paper
		filename -- the file name
		"""
		
		self.text = title
		self.filepath = filepath
		self.filename = filename
		self.matches = []
		camelcase = re.compile("([a-z][A-Z0-9])|([0-9][a-zA-Z])")
		self.searchterm = camelcase.sub((lambda m: m.group()[0] + " " + m.group()[1]), filename)
	
	def add_match(self, pattern, text):
		"""
		Add a match.
		
		Arguments:
		pattern -- the matching pattern
		text -- the matching text
		"""
		
		match = Match(pattern, text)
		self.matches.append(match)
		return match

	def get_patterns(self):
		"""
		Return the set of matching patterns.
		"""
		
		return set([m.pattern for m in self.matches])

wordsplitter = Wordsplitter()

class Match:
	"""
	Container for a match.
	"""
	
	def __init__(self, pattern, text):
		"""
		Arguments:
		pattern -- the matching pattern
		text -- the matching text
		"""
		
		self.pattern = pattern
		self.text = text
		
	def trim(self):
		"""
		Correctly format fullstops.
		"""
		
		if self.text[0] == "." and self.text[-1] == ".":
			self.text = self.text[2:-2] + "."
		
	def mark(self, to_mark):
		"""
		Mark words in text.
		"""
		
		for i,k in to_mark: 
			self.text[i] = self.__mark_start(self.text[i])
			j = i+k-1
			self.text[j] = self.__mark_end(self.text[j])
		
		self.text = " ".join(self.text).decode("utf-8")

	def __mark_match_object(self, mo):
		"""
		Mark a certain match inside a match object.
		"""
		
		text = mo.group()
		return text[:mo.start("match")-mo.start()] + self.__mark(mo.group("match")) + text[- (mo.end() - mo.end("match")):]
	
	def __mark_start(self, text):
		return '<span class="token">' + text
	
	def __mark_end(self, text):
		return text + '</span>'
	
	def __mark(self, text):
		"""
		Apply HTML to mark a text.
		"""
		
		return '<span class="token">{}</span>'.format(text)
