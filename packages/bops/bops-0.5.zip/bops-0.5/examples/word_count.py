from bops import bop
import re

text = """
bops stands for boolean array operations.
bops uses numpy to do boolean operations on numpy.ndarrays.
This module is meant to simpifiy boolean operations on lists and arrays.
This module also allows for combining boolean arrays to get the logical AND,
as well as the OR, for multiple boolean arrays.
This functionality allows for faster data filtering on multiple aspects of the data.
"""

#remove puncuation
text = re.sub(r'\.|,|!|:|;', '', text)

#split on spaces and remove newlines
w = [(a.lower().strip(),) for a in text.split(' ')]

# create bop instance
word_count = bop(w, 'word')

#map function for finding unique words
def unique_words_mapper(row):
	return row.word, 1

#run map reduce job, using sum as the reducer
word_count_results = word_count.mapreduce(unique_words_mapper, sum, expand=True)

# top 5 words
print "\nTop 5 words: "
for i, (w, c) in enumerate(sorted(word_count_results, key=lambda kv: -kv[1])[:5]):
	print str(i+1)+". " +str(c)+" - "+w
print

#loop through all results, sorted on count in descending order (higher values first)
# for word, count in sorted(word_count_results, key=lambda kv: -kv[1]):
	# print word, count

#mapping on first letter
def startswith_mapper(row):
	return row.word[0], row

# group words on the letter they start with
startwith_results = word_count.mapreduce(startswith_mapper, len, expand=True, sort=True)

# show startswith results
print "Startswith results: "
for letter, count in sorted(startwith_results, key=lambda kv: -kv[1]):
	print letter, count
print


print "\nDone."

