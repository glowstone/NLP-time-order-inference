from nltk.metrics.distance import edit_distance
from nltk import pos_tag, word_tokenize, ne_chunk


COORD_CONJS = ["'til'", 'after', 'although', 'as', 'as if', 'as long as', 'as much as', 'as soon as', 'as though',
 'because', 'before', 'even if', 'even though', 'how', 'if', 'in order that', 'inasmuch', 'lest', 'now that',
 'provided', 'since', 'so that', 'than', 'that', 'though', 'till', 'unless', 'until', 'when', 'whenever', 'where',
 'wherever', 'while']


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


def event_compare(event, text):
	"""
	Computes a score of similarity between event and text. This is calculated on two metrics:
		1. The number of common words between text and event.text
		2. The percentage of entities in event.entities that also occur as words in the text
	A higher score means a closer match.

	event is an instance of an AbstractEvent
	text is a string

	returns: a tuple of (float, float)
	"""
	# print event.text
	text = text.lower()
	# base_score is the levenshtein distance between text and event.text, divided by the number of words in event.text
	base_score = len(event.text.split()) - edit_distance(event.text.lower().split(), text.split())
	# entity_match_score is the percentage of entities in event.entities that occur in the text
	entity_match_score = sum([entity.lower() in text for entity in event.entities])
	print base_score, entity_match_score
	return (base_score, entity_match_score)


def event_match(events, text):
	"""
	Given a list of AbstractEvents, finds the AbstractEvent e that maximizes the score returned by 
	event_compare(e, text).

	events is a list of AbstractEvents
	text is a string

	returns: an AbstractEvent
	"""
	score = 0		# Set this to something above 0 to have it as the minimum score, the threshold
	best_event = None
	for event in events:
		# print event
		new_score, entity_score = event_compare(event, text)
		if entity_score == 0:
			continue
		if new_score > score:
			# print new_score, score
			score = new_score
			best_event = event
	threshold = len(best_event.text.split())/10.0
	if score < threshold:	# Threshold value of 10% of the length of the event's text
		print "Event score %s not above threshold %s" % (score, threshold)
		return None
	print "Best score: %s" % score
	return best_event


def extract_entities(event):
	"""
	Given an AbstractEvent, finds all named entities in the text of the event.

	event is an instance of an AbstractEvent.

	returns: A list of strings
	"""
	# TODO The text should probably already be tagged and tokenized before this step
	tree = ne_chunk(event.pos_tagged)
	entities = set([])

	people = tree.subtrees(lambda x: x.node == "PERSON")
	for person in people:
		entities.add(" ".join([leaf[0] for leaf in person.leaves()]))

	places = tree.subtrees(lambda x: x.node == "GPE")
	for place in places:
		entities.add(" ".join([leaf[0] for leaf in place.leaves()]))

	organizations = tree.subtrees(lambda x: x.node == "ORGANIZATION")
	for org in organizations:
		entities.add(" ".join([leaf[0] for leaf in org.leaves()]))
	
	return entities