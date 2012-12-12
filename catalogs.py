

# Leading Clue Words
###############################################################################
# Chronological Leading Word
CHRON_LEAD = ["later", "afterward", "next", "then", "later"]
# Anti-Chronological Leading Word
ACHRON_LEAD = ["previously", "beforehand", "earlier"]


# Subordinating Conjunction Clue Words
###############################################################################
# A before B
CHRON_CONJS = ["before", "until", "till", "til", "so that"]
# A simultaneous with B
DURING_CONJS = ["as", "during", "as long as", "when", "whenever", "while"]
# A after B
ACHRON_CONJS = ["after", "now that", "as soon as", "since"]



class WordCatalog(object):
	def __init__(self, name, items, initial_score=0):
		self.name = name                       # Useful WordCatalog name
		self.items = items                     # Exhaustive list of words in the catalog                                    
		self.initial_score = initial_score     # initial_score used to prefer one WordCatalog over another

	def get_name(self):
		"""returns the string name of the WordCatalog type"""
		return self.name

	def __repr__(self):
		return '<ScoredCatalog %s>' % self.name