

# Cross Sentence Lead Words
###############################################################################
CROSS_CHRON_LEAD = ["later", "afterward", "next", "then", "later"]    # chronological
CROSS_ACHRON_LEAD = ["previously", "beforehand", "earlier"]           # anti-chronological

# Same Sentence Lead Words  Ex. (After X, then Y happened. -> X before Y)
###############################################################################
CHRON_LEAD = ['after']            # A before B
ACHRON_LEAD = ['before']          # B before A

# Same Sentence Conjunction Words
###############################################################################
CHRON_CONJS = ["before", "until", "till", "til", "so that"]                  # A before B
DURING_CONJS = ["as", "during", "as long as", "when", "whenever", "while"]   # A simultaneous with B
ACHRON_CONJS = ["after", "now that", "as soon as", "since"]                  # A after B


class ScoredCatalog(object):
	def __init__(self, name, items, initial_score=0.0):
		self.name = name                   # Useful WordCatalog name
		self.items = items                 # Exhaustive list of words in the catalog                                    
		self.score = float(initial_score)  # Score stores the score of the catalog

	def get_name(self):
		"""
		returns the string name of the WordCatalog type
		"""
		return self.name

	def get_score(self):
		"""
		returns the float score
		"""
		return self.score

	def increment_score(self, increment):
		"""
		Increments the score of the ScoredCatalog
		returns None
		"""
		self.score += increment

	def __repr__(self):
		return '<ScoredCatalog %s>' % self.name