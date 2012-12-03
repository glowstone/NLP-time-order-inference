from nltk.metrics.distance import edit_distance
from nltk import pos_tag, word_tokenize, ne_chunk


COORD_CONJS = ["after", "how", "till", "'til'", "although", "if", "unless", "as", "inasmuch", "until", "as if", 
"in order that", "when", "as long as", "lest", "whenever", "as much as", "now that", "where", "as soon as", 
"provided", "wherever", "as though", "since", "while", "because", "so that", "before", "than", "even if", 
"that", "even though", "though"]


def sentence_distance(s1, s2):
	"""
	Computes the Levenshtein Distance (in words) between two sentences s1 and s2.
	s1 and s2 are both strings
	returns: int, the number of edits that must be made for s1 and s2 to be equal
	"""
	s1 = word_tokenize(s1)	# Convert them both into lists of words, so that the edit distance is computed
	s2 = word_tokenize(s2)	# in words instead of in characters
	return edit_distance(s1, s2)


def pos_tag_sentence(sentence):
	"""
	Just a wrapper around nltk.pos_tag. Using this as an abstraction layer so that we could theoretically change
	how our POS tagging works without too much effort elsewhere.

	sentence is a string.
	returns: list of tuples, with each tuple containing (word, tag) for each word in the sentence.
	"""
	return pos_tag(word_tokenize(sentence))


def entity_tag_sentence(sentence):
	"""
	Just a wrapper around nltk.ne_chunk. Using this as an abstraction layer so that we could theoretically change
	how our entity tagging works without too much effort elsewhere.

	sentence is a POS tagged sentence, as returned by nltk.pos_tag
	"""
	return ne_chunk(sentence)