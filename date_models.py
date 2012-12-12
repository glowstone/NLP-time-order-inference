from datetime import datetime


MONTH_TO_STRING = ['No month', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
				   'Novermber', 'December']


class Date():
	def __init__(self, year=None, month=None, day=None, hour=None, minute=None):
		self.year = year
		self.month = month
		self.day = day
		self.hour = hour
		self.minute = minute

	def __lt__(self, other):
		"""
		Tries to determine if self < other. While doing so, it tries to resolve ambiguities and admit when it can't
		determine whether one is less than the other.

		other is a Date object

		returns: boolean or "Can't tell" if it can't tell
		"""
		rep = [self.year, self.month, self.day, self.hour, self.minute]
		other_rep = [other.year, other.month, other.day, other.hour, other.minute]
		rep2 = []
		other_rep2 = []

		for i in xrange(len(other_rep)):
			item1 = rep[i]
			item2 = other_rep[i]

			# Basically going to iterate through rep and other_rep, and compare the parts that are present in both of
			# them. If anything is ambiguous, return "Can't tell"
			if item1 is None:
				if item2 is not None:
					if rep2 == other_rep2:
						# It's been equal up to this point, but now other is more specific than self so they
						# kind of happened at the same time
						return "Can't tell"
				# Year was not defined for either, so we can't really do much
				if rep2 == [] and other_rep2 == []:
					return "Can't tell"
				return rep2 < other_rep2

			if item2 is None:
				if item1 is not None:
					if rep2 == other_rep2:
						# It's been equal up to this point, but now self is more specific than other so they
						# kind of happened at the same time
						return "Can't tell"
				# Year was not defined for either, so we can't really do much
				if rep2 == [] and other_rep2 == []:
					return "Can't tell"
				return rep2 < other_rep2

			else:	# Otherwise they both have this item, so we can append it and continue
				rep2.append(item1)
				other_rep2.append(item2)
				
		# This is the case where both had all 5 defined, then just compare the lists.
		return rep2 < other_rep2


	def __gt__(self, other):
		return other.__lt__(self)

	def __eq__(self, other):
		return [self.year, self.month, self.day, self.hour, self.minute] == [other.year, other.month, other.day, other.hour, other.minute]

	def __repr__(self):
		return "Date %s %s %s %s %s" % (self.year, self.month, self.day, self.hour, self.minute)

	def __str__(self):
		string = ""
		if self.month is not None:
			string += MONTH_TO_STRING[self.month]
			if self.day is not None:
				string += " "
				string += str(self.day)
			if self.year is not None:
				string += ", "
				string += str(self.year)
			if self.hour is not None:
				string += " at "
				string += str(self.hour)
				if self.minute is not None:
					string += ":%2d" % self.minute
				else:
					string += ":00"
		else:
			if self.year is not None:
				string = "Some time in %s" % self.year
				if self.hour is not None:
					string += " at %s" % self.hour
					if self.minute is not None:
						string += ":%2d" % self.minute
					else:
						string += ":00"
		if string == "":
			string = "Not really sure"
		return string

	def precision(self):
		"""
		Returns a measure of how precise this Date object is, allowing Dates to be sorted on their precision.
		The reason for doing it in powers of 10 is that it was an easy way to show that some values add more
		to the precision than others, rather than just returning the number of fields that aren't None.
		"""
		value = 0
		if self.year is not None:
			value += 100000
		if self.month is not None:
			value +=  10000
		if self.day is not None:
			value +=   1000
		if self.hour is not None:
			value +=    100
		if self.minute is not None:
			value +=     10
		return value

	def to_datetime(self):
		"""
		Build a datetime object for the time represented by this Date object. Since there is ambiguity (e.g. day may
		not be defined for this Date object), the method also returns a dictionary saying which of the fields in the
		datetime object are actually accurate. For example, if self.day == None, then we shouldn't trust
		datetime.day either, so we keep track of which ones should be trusted and which ones need to be ignored.

		returns: a tuple of (datetime, dictionary) where dictionary says which fields of the datetime can be trusted
		"""
		dt = datetime.now()
		trusted = {'year': False, 'month': False, 'day': False, 'hour': False, 'minute': False}
		if self.year is not None:
			dt = dt.replace(year=int(self.year))
			trusted['year'] = True
		if self.month is not None:
			dt = dt.replace(month=int(self.month))
			trusted['month'] = True
		if self.day is not None:
			dt = dt.replace(day=int(self.day))
			trusted['day'] = True
		if self.hour is not None:
			dt = dt.replace(hour=int(self.hour))
			trusted['hour'] = True
		if self.minute is not None:
			dt = dt.replace(minute=int(self.minute))
			trusted['minute'] = True
		return (dt, trusted)
