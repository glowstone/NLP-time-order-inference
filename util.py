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
		1. The levenshtein distance between event.text and text, divided by the number of words in event.text
		2. The percentage of entities in event.entities that also occur as words in the text
	A higher score means a closer match.

	event is an instance of and AbstractEvent
	text is a string

	returns: a tuple of (float, float)
	"""
	# print event.text
	text = text.lower()
	# base_score is the levenshtein distance between text and event.text, divided by the number of words in event.text
	base_score = 1 - edit_distance(event.text.lower().split(), text.split())/float(len(event.text.split()))
	# entity_match_score is the percentage of entities in event.entities that occur in the text
	entity_match_score = sum([entity.lower() in text for entity in event.entities])/float(len(event.entities))
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
	score = event_compare(events[0], text)[0]
	best_event = events[0]
	for event in events[1:]:
		# print event
		new_score = event_compare(event, text)[0]
		if new_score > score:
			# print new_score, score
			score = new_score
			best_event = event
	return best_event


def extract_entities(event):
	"""
	Given an AbstractEvent, finds all named entities in the text of the event.

	event is an instance of an AbstractEvent.

	returns: A list of strings
	"""
	# TODO The text should probably already be tagged and tokenized before this step
	tree = ne_chunk(event.pos_tagged)
	entities = []

	people = tree.subtrees(lambda x: x.node == "PERSON")
	for person in people:
		entities.extend([leaf[0] for leaf in person.leaves()])

	places = tree.subtrees(lambda x: x.node == "GPE")
	for place in places:
		entities.extend([leaf[0] for leaf in place.leaves()])

	organizations = tree.subtrees(lambda x: x.node == "ORGANIZATION")
	for org in organizations:
		entities.extend([leaf[0] for leaf in org.leaves()])
	
	return entities