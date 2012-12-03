import urllib
import urllib2
from BeautifulSoup import BeautifulSoup

url = 'http://nlp.stanford.edu:8080/parser/index.jsp'
user_agent = 'Dolphins!!!'
header = { 'User-Agent' : user_agent }

values = {'query': 'Sarah traveled home after Alice got back from the galleria .'}

data = urllib.urlencode(values)
# req = urllib2.Request(url+data, None, header) # GET works fine
req = urllib2.Request(url, data, header)  # POST request doesn't not work

response = urllib2.urlopen(req)

htmlSource = response.read()   

soup = BeautifulSoup(htmlSource)

answer = soup.find("pre", {"id": "parse"})
answer2 = answer.text

import nltk
tree = nltk.tree.Tree(answer2)

print list(tree.subtrees(lambda x: x.node == "SBAR"))[0].leaves()






      

