class Date():
	def __init__(self, year=None, month=None, day=None, hour=None, minute=None):
		self.year = year
		self.month = month
		self.day = day
		self.hour = hour
		self.minute = minute

	def __lt__(self, other):
		rep = [self.year, self.month, self.day, self.hour, self.minute]
		other_rep = [other.year, other.month, other.day, other.hour, other.minute]
		rep2 = []
		other_rep2 = []

		# Basically we need to get rid of cases where we're trying to compare something like "2003" with "January 5".
		# In that case, we really can't do anything so we'll return "Can't tell". But, if it's like comparing "2003"
		# with "January 5, 2002" then we should do the comparison on the years. The following basically gets rid of
		# the fields that they don't both have, and compares what's left over if possible
		for i in xrange(len(rep)):
			if rep[i] is not None and other_rep[i] is not None:
				rep2.append(rep[i])
				other_rep2.append(other_rep[i])
			elif rep[i] is None and other_rep[i] is None:
				continue
			else:
				break

		print rep2, other_rep2
		if not (rep2 and other_rep2):
			return "Can't tell"
		for i in xrange(len(rep2)):
			if rep2[i] is not None:
				if other_rep2[i] is None:
					return "Can't tell"
			else:
				if other_rep2[i] is not None:
					return "Can't tell"

		return rep < other_rep

	def __gt__(self, other):
		return other.__lt__(self)

	def __repr__(self):
		return "Date %s %s %s %s %s" % (self.year, self.month, self.day, self.hour, self.minute)