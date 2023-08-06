import re
class RegularExpression:

	def __init__(self, input):
		self.string = input
		self.regex = re.compile(input)

	def match(self, input):
		match = self.regex.search(input)
		if match is not None:
			return Match(match)
		else: return None

class Match:
	def __init__(self, matchObject):
		self.match = matchObject

	def __getitem__(self, key):
		return self.match.group(key)