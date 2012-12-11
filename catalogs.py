

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



class CustomCatalog(object):
	def __init__(self, items, chronological=False, initial_score=0):
		self.items = items                         # Exhaustive list of words in the catalog
		# Boolean of whether this a catalog of words corresponding to chronological ordering of events
		self.chron = chronological                 
		self.initial_score = initial_score         # initial_score used to prefer one Catalog over another

	def get_chron(self):
		"""returns the chron property of the CustomCatalog"""
		return self.chron

	def __repr__(self):
		return '<CustomCatalog %s>' % self.chron