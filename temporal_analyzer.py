
import sys
import timex
import getopt

class TemporalAnalyzer(object):

	def __init__(self, filename, config):


		self.internal = []


	def process_text(filename=None):
		"""
		Takes in the input file and builds the DataStructure to support queries
		Assumptions:"""
		pass

	def get_events():
		"""
		Returns an unordered array of all events found in the text"""
		pass


	def estimate_time(event_id):
		"""Returns the best available information about Event event_id"""
		pass

	def estimate_order(event_id):
		"""Returns the estimate of the order of the Event with event_id"""



if __name__ == "__main__":
	try:
		options, remaining = getopt.gnu_getopt(sys.argv[1:], "f:s:v", ["filename=", "start=", "verbose"])
	except getopt.GetoptError:
		# Invalid Argument was provided
		print "python temporal_analysis.py -f <filename> [-v / --verbose] [-s ISO / --start ISO]"
		sys.exit(2)

	config = {"start_mode": False,
			  "start": None,
			  "verbose_mode": False}
	for option in options:
		name, argument = option
		if name == '-f' or name == 'filename':
			filename = argument
		if name == '-v' or name == '--verbose':
			config['verbose_mode'] = True
		if name == '-s' or name == '--start':
			config['start_mode'] = True
			config['start'] = argument

	#Create a TemporalAnalyzer instance
	analyzer= TemporalAnalyzer(filename, config)
	print analyzer

	# Analyzer now supports queries