# Code for tagging temporal expressions in text
# For details of the TIMEX format, see http://timex2.mitre.org/

import re
import string
import os
import sys
from datetime import datetime
from dateutil import parser


# Predefined strings.
month = "(january|february|march|april|may|june|july|august|september|\
october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|sept|\
oct|nov|dec)"
iso = "\d+[/-]\d+[/-]\d+ \d+:\d+:\d+\.\d+"
year = "((?<=\s)\d{4}|^\d{4})"

time = "((((\d{1,2})(:\d{0,2})?) ?(A\.?M\.?|P\.?M\.?))|((\d{1,2})(:\d{2})))"
# date = "(%s\.? \d{0,2}?,? ?\d{4}?)" % month

month_day_year = "(%s\.? \d{1,2} ?,? ?\d{4}?)" % month
month_day = "(%s\.? \d{1,2})" % month
month_year = "(%s\.? ?\d{4}?)" % month


iso_regex = re.compile(iso)                      # matches iso formats
year_regex = re.compile(year)						# matches 4-digit years
time_regex = re.compile(time, re.IGNORECASE)	# Matches 9:00, 9:00PM, 9:00 PM, 9PM, 9 PM but not just 9
month_day_year_regex = re.compile(month_day_year, re.IGNORECASE)	# matches January 24, 2009; Jan. 24 2009 etc.
month_day_regex = re.compile(month_day, re.IGNORECASE)				# matches January 24; Jan. 24 etc.
month_year_regex = re.compile(month_year, re.IGNORECASE)			# matches January 2009; Jan. 2009 etc.
# date_regex = re.compile(date, re.IGNORECASE)

def find_temporals(text):
	"""
	Takes a string (text) and finds matches for the regexes defined above. It starts with the most specific and moves
	to the most general, so that if a string like "January 24, 2003" appears in the text, it will only be tagged once
	(as a month_day_year) instead of once for January 24, once for 2003, and once for the whole thing. Each time a
	a match is found, the matching part of the string is added to a list corresponding to its accuracy/precision.

	returns: a list of Date objects
	"""
	# The order the regexes appear in this function is the order of precedence they should take over one another

	# Initialization
	times_found = []
	# dates_found = []
	month_day_years_found = []
	month_days_found = []
	month_years_found = []
	years_found = []
	iso_found = []

	# Time
	found = time_regex.findall(text)
	for timex in found:
		times_found.append(timex[0])    # Append the first capture group

	found = month_day_year_regex.findall(text)
	for timex in found:
		month_day_years_found.append(timex[0])
		text = text.replace(timex[0], "")

	found = month_year_regex.findall(text)
	for timex in found:
		month_years_found.append(timex[0])
		text = text.replace(timex[0], "")

	found = month_day_regex.findall(text)
	for timex in found:
		month_days_found.append(timex[0])
		text = text.replace(timex[0], "")

	# Year
	found = year_regex.findall(text)
	for timex in found:
		years_found.append(timex)
		text = text.replace(timex, "")

	# ISO
	found = iso_regex.findall(text)
	for timex in found:
		iso_found.append(timex)
		text = text.replace(timex, "")

	datetimes = []

	# If there is at least one date and at least one time, try combining them into a date plus a time
	if len(times_found) > 0:
		if len(month_day_years_found) > 0:
			date_time_str = month_day_years_found.pop(0) + " " + times_found.pop(0)
			date = parse_datetime(date_time_str)
			date2 = Date(year=date.year, month=date.month, day=date.day, hour=date.hour, minute=date.minute)
			datetimes.append(date2)

		elif len(month_years_found) > 0:
			date_time_str = month_years_found.pop(0) + " " + times_found.pop(0)
			date = parse_datetime(date_time_str)
			date2 = Date(year=date.year, month=date.month, hour=date.hour, minute=date.minute)
			datetimes.append(date2)

		elif len(month_days_found) > 0:
			date_time_str = month_days_found.pop(0) + " " + times_found.pop(0)
			date = parse_datetime(date_time_str)
			date2 = Date(month=date.month, day=date.day, hour=date.hour, minute=date.minute)
			datetimes.append(date2)

	# Don't know anything about the hour or minutes
	for date in month_day_years_found:
		datetime = parse_datetime(date)
		datetimes.append(Date(year=datetime.year, month=datetime.month, day=datetime.day))

	# Don't know anything about days, hours, or minutes
	for date in month_years_found:
		datetime = parse_datetime(date)
		datetimes.append(Date(year=datetime.year, month=datetime.month))

	# Don't know anything about year, hours, or minutes
	for date in month_days_found:
		datetime = parse_datetime(date)
		datetimes.append(Date(month=datetime.month, day=datetime.day))

	# Only know the year
	for year in years_found:
		datetimes.append(Date(year=year))

	# Only know the time (hours and minutes)
	for time in times_found:
		datetime = parse_datetime(time)
		datetimes.append(Date(hour=datetime.hour, minute=datetime.minute))

	return datetimes


# Use the nice dateutil.parser to figure out the relevant information from the string.
def parse_datetime(date_string):
	try:
		date = parser.parse(date_string)
		return date
	except ValueError:
		return None


class Date():
	def __init__(self, year=None, month=None, day=None, hour=None, minute=None):
		self.year = year
		self.month = month
		self.day = day
		self.hour = hour
		self.minute = minute

	def __lt__(self, other):
		return [self.year, self.month, self.day, self.hour, self.minute] < \
		[other.year, other.month, other.day, other.hour, other.minute]		# TODO does this work?

	def __gt__(self, other):
		return other.__lt__(self)

	def __repr__(self):
		return "Date %s %s %s %s %s" % (self.year, self.month, self.day, self.hour, self.minute)


if __name__ == '__main__':
	print find_temporals("John went to the store at 7:00pm yesterday .")