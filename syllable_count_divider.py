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
			# pdb.set_trace()
			result[i[0]][i[3]] += 1
	return result

def rhyme_to_POS(sentances):
	result = defaultdict(lambda : defaultdict(defaultdict))
	tagged_tweets = CMU.runtagger_parse(sentances)
	for tweet in tagged_tweets:
		for word in tweet:
			cur_word = word[0]
			tag = word[1]
			info = test.get_words_info(cur_word)[0]
			rhyme = info[1]
			syl_count = info[0]
			# if result[rhyme][tag][syl_count] != None:
			cur = result[rhyme][tag].setdefault(syl_count, Counter())
			cur[cur_word] += 1
			# else:
			# 	result[rhyme][tag][syl_count] = [cur_word]
	return result



with open(sys.argv[1]) as f:
	lines = f.readlines()
pp = pprint.PrettyPrinter(indent=4)
res = rhyme_to_POS(lines)
pp.pprint(res)

