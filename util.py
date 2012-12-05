from nltk.metrics.distance import edit_distance
from nltk import pos_tag, word_tokenize, ne_chunk


COORD_CONJS = ["'til'", 'after', 'although', 'as', 'as if', 'as long as', 'as much as', 'as soon as', 'as though',
 'because', 'before', 'even if', 'even though', 'how', 'if', 'in order that', 'inasmuch', 'lest', 'now that',
 'provided', 'since', 'so that', 'than', 'that', 'though', 'till', 'unless', 'until', 'when', 'whenever', 'where',
 'wherever', 'while']


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
	returns: ordered list of tuples, with each tuple containing (word, tag) for each word in the sentence.
	"""
	return pos_tag(word_tokenize(sentence))


def entity_tag_sentence(sentence):
	"""
	Just a wrapper around nltk.ne_chunk. Using this as an abstraction layer so that we could theoretically change
	how our entity tagging works without too much effort elsewhere.

	sentence is a POS tagged sentence, as returned by nltk.pos_tag
	"""
	return ne_chunk(sentence)