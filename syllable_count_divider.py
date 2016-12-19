from TwitterSearch import *  #code from https://github.com/ckoepp/TwitterSearch
import test
import subprocess
import unicodedata
import SpecialCharacters
import pdb
import pprint
import CMUTweetTagger as CMU
import re
import sys
import string
from collections import defaultdict
from collections import Counter

def syl_to_word(sentances):
	result = defaultdict(Counter)
	for sentance in sentances:
		info = test.get_words_info(sentance)
		for i in info:
			result[i[0]][i[3]] += 1
	return result

# the input for this program is tagged tweets.
# returns a list of rhyme families with possible
# POS tags for the rhyme families with syllable counts,
# that go to words with that syllable count
# rhyme --> POS --> syllable count --> words
def rhyme_to_POS(sentances):
	result = defaultdict(lambda : defaultdict(defaultdict))
	tagged_tweets = sentances
	# for each tweet
	for tweet in tagged_tweets:
		for word in tweet:
			cur_word = word[0]
			tag = word[1]
			# skip all urls
			if (tag == "U"):
				continue
			info = test.get_words_info(cur_word)[0]
			# collect the rhyme of out current word
			rhyme = info[1]
			syl_count = info[0]
			# place it into list, under the current
			# syllable count, rhyme, and tag
			cur = result[rhyme][tag].setdefault(syl_count, [])
			cur.append(cur_word)
			
	return result




