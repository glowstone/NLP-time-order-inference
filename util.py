
import sys, os
import urllib
import urllib2
from BeautifulSoup import BeautifulSoup
from nltk.metrics.distance import edit_distance
from nltk import pos_tag, word_tokenize, ne_chunk
from nltk.corpus import stopwords

# Local Modules
import config
from timex import tag, ground
from date_models import Date
from catalogs import ScoredCatalog, CHRON_LEAD, ACHRON_LEAD, CHRON_CONJS, ACHRON_CONJS, \
CROSS_CHRON_LEAD, CROSS_ACHRON_LEAD


ENGLISH_STOPWORDS = stopwords.words("english")


# Wrappers for NLTK / Parsing Functionalities
###############################################################################

def entity_tag_sentence(sentence):
    """
    Wrapper around nltk.ne_chunk. Abstraction here allows changing entity tagger later if desired.

    sentence is a POS tagged sentence, as returned by nltk.pos_tag
    """
    return ne_chunk(sentence)


def stanford_parse(sentence):
    """
    Make a POST request to the stanford parser and extract the parse information from the webpage.

    sentence is a string with just the plain text of the sentence.
    returns: A string representing the parse, using the (S (NP (...))) notation
    """
    #user_agent = 'Please build an API'
    #header = { 'User-Agent' : user_agent }

    values = {'query': sentence}
    data = urllib.urlencode(values)
    request = urllib2.Request(config.STANFORD_PARSE_URL, data, {})

    response = urllib2.urlopen(request)
    htmlSource = response.read()

    # Get the text of the parse from the html response
    soup = BeautifulSoup(htmlSource)
    parse = soup.find("pre", {"id": "parse"}).text

    return parse


# Other Utilities
###############################################################################

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

    # Filter out stop words
    text2 = filter(lambda x: x not in ENGLISH_STOPWORDS, event.text.lower().split())

    base_score = edit_distance(text2, text)
    base_score = max((len(text) - base_score, len(text2) - base_score))
    # base_score = sum([w in text2 for w in text])
    # entity_match_score is the percentage of entities in event.entities that occur in the text
    entity_match_score = sum([entity.lower() in text for entity in event.entities])
    # print base_score, entity_match_score
    return (base_score, entity_match_score)


def best_event_match(events, text, threshold_percentage):
    """
    Given a list of AbstractEvents, finds the AbstractEvent e that maximizes the score returned by 
    event_compare(e, text).

    events is a list of AbstractEvents
    text is a string
    threshold_percentage is the value multiplied by the length of the event text to get the threshold score

    returns: an AbstractEvent, or None if no matching event was found
    """
    # Filter out short, stop words
    text = filter(lambda x: x not in ENGLISH_STOPWORDS, text.lower().split())

    score = 0
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

    if not best_event:
        return None

    threshold = len(best_event.text.split())*threshold_percentage
    if score < threshold:   
        # print "Event score %s not above threshold %s" % (score, threshold)
        return None

    # print "For match %s,  %s" % (text, best_event.text)
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


def cross_sent_order(lead_words):
    """
    Infer whether the first or second Event occurred first using leading word and conjunction word
    observations

    returns name of a catalog such as 'chron', 'achron', or 'unordered' indicating correct ordering.
    """
    lead_catalogs = [ScoredCatalog('chron', CROSS_CHRON_LEAD), ScoredCatalog('achron', CROSS_ACHRON_LEAD)]
    unordered_catalog = ScoredCatalog([], 'unordered', 0.5)

    lead_decision = max([score_catalog_match(catalog, lead_words) for catalog in lead_catalogs], key=lambda catalog: catalog.get_score())
    unordered_decision = score_catalog_match(unordered_catalog, [])

    # Determine the dominant chronology decision by comparing catalog scores
    winning_catalog = max([unordered_decision, lead_decision], key=lambda catalog: catalog.get_score())
    print winning_catalog, winning_catalog.get_score()
    return winning_catalog.get_name()


def same_sent_order(lead_words, conj_words):
    """
    Infer whether the first or second Event occurred first using leading word and conjunction word
    observations

    returns name of a catalog such as 'chron', 'achron', or 'unordered' indicating correct ordering.
    """
    lead_catalogs = [ScoredCatalog('chron', CHRON_LEAD), ScoredCatalog('achron', ACHRON_LEAD)]
    conj_catalogs = [ScoredCatalog('chron', CHRON_CONJS), ScoredCatalog('achron', ACHRON_CONJS)]
    unordered_catalog = ScoredCatalog([], 'unordered', 0.5)

    # Decide among the chronological and anti-chronological catalogs for lead words and conj words
    lead_decision = max([score_catalog_match(catalog, lead_words) for catalog in lead_catalogs], key=lambda catalog: catalog.get_score())
    conj_decision = max([score_catalog_match(catalog, conj_words) for catalog in conj_catalogs], key=lambda catalog: catalog.get_score())
    unordered_decision = score_catalog_match(unordered_catalog, [])

    # Determine the dominant chronology decision by comparing catalog scores
    winning_catalog = max([unordered_decision, lead_decision, conj_decision], key=lambda catalog: catalog.get_score())
    print winning_catalog, winning_catalog.get_score()
    return winning_catalog.get_name()


def score_catalog_match(catalog, observed):
    """
    Find all matching subsequences between the catalog list of words and the list of observed
    words and increments the catalogs score for each found.
    Scores the given catalog based on matches found with observations

    observed is list of observed words such as ['now', 'that']
    returns the catalog, with its score now updated
    """
    for catalog_word in catalog.get_items():
        for observed_word in observed:
            if catalog_word.lower() == observed_word.lower():
                catalog.increment_score(1)
    return catalog


    # score = catalog.initial_score                  # Chronological orderings favored over anit-chronological orderings
    # for catalog_item in catalog.items:
    #   # Assume for now that the catalog item is one word to be matched. TODO fix.
    #   for observed_item in observed:
    #       if catalog_item.lower() == observed_item.lower():
    #           score += 1
    # return (score, catalog)
    #score = sum(exact_match(observed_item, catalog_item) for observed_item in observed)

    #return score

def aux_phrase_subtree(tree, tag_list):
    """
    Searches over all subtrees in the given tree that have a root node with a tag in tag_list

    returns subtree with the greatest height that is not the original tree
    """
    highest_subtree = max([(0, None)]+[(subtree.height(), subtree) for subtree in tree.subtrees(lambda x: x.node in tag_list) if subtree != tree[0]])[1]
    # print highest_subtree
    return highest_subtree

def error(message):
    """
    User error has occurred
    """
    print message
    sys.exit(2)


# General Utility Functions
###############################################################################

def subsequence_search(subseq, sequence):
    """
    Performs naive subsequence searching.

    Input list subseq and sequence 

    returns a list of (start, end) tuples of indices such that sequence[start:end] == subseq
    """
    index_tuples = filter(lambda (start, end): sequence[start:end] == subseq, [(start,start+len(subseq)) for start in range(len(sequence) - len(subseq) + 1)])
    return index_tuples


def nested_access(nested_list, indices):
    """
    Recursive list multi-index access. 

    Given for ex. nested_access(nested_list, [0,1,3]), returns result of nested_list[0][1]][3]
    """
    if len(indices) > 0:
        return nested_access(nested_list[indices[0]], indices[1:])
    else:
        return nested_list


def nested_pop(nested_list, indices):
    """
    Recursive list multi-index popping. 

    Given for ex. nested_pop(nested_list, [0,1,3]), returns will perform nested_list[0][1]].pop(3)
    """
    if len(indices) > 1:
        return nested_pop(nested_list[indices[0]], indices[1:])
    else:
        return nested_list.pop(indices[0])


def event_timex_analysis(event1, event2):
        """
        Attempts to use timex.tag and timex.ground to find relations like "two weeks before". If this ReferenceEvent
        refers to an event with an absolute time, then we can use the "two weeks before" to figure out exactly what
        time that means.
        """
        tagged = tag(event1.text)
        base_time = event1.get_best_time()

        if base_time is not None:
            dt, trusted = base_time.to_datetime()   # Get the datetime representation of the reference's best_time
            grounded_times = ground(tagged, dt)     # Ground any timex tags to that time
            new_dates = []                          # holds new dates constructed from the grounded datetimes

            for time in grounded_times:
                new_date = Date()
                if trusted['year']:
                    new_date.year = time.year

                if trusted['month']:
                    new_date.month = time.month

                if trusted['day']:
                    new_date.day = time.day

                if trusted['hour']:
                    new_date.hour = time.hour

                if trusted['minute']:
                    new_date.minute = time.minute

                new_dates.append(new_date)

            if len(new_dates) == 0:     # Nothing interesting found.
                return

            new_dates = sorted(new_dates, lambda x: x.precision(), reverse=True)
            best_date = new_dates[0]

            other_best_date = event2.get_best_time()
            if other_best_date is not None:
                if best_date.precision() > other_best_date.precision():
                    event2.set_best_time(best_date)
            else:
                event2.set_best_time(best_date)

