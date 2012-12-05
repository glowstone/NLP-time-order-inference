import urllib
import urllib2
from BeautifulSoup import BeautifulSoup

url = 'http://nlp.stanford.edu:8080/parser/index.jsp'
user_agent = 'Dolphins!!!'
header = { 'User-Agent' : user_agent }

def get_parse(sentence):
	"""
	Make a POST request to the stanford parser and extract the parse information from the webpage.

	sentence is a string with just the plain text of the sentence.
	returns: A string representing the parse, using the (S (NP (...))) notation
	"""
	values = {'query': sentence}
	data = urllib.urlencode(values)
	request = urllib2.Request(url, data, header)

	response = urllib2.urlopen(request)
	htmlSource = response.read()

	# Get the text of the parse from the html response
	soup = BeautifulSoup(htmlSource)
	parse = soup.find("pre", {"id": "parse"}).text

	return parse

	# tree = nltk.tree.Tree(parse)

	# print list(tree.subtrees(lambda x: x.node == "SBAR"))[0].leaves()