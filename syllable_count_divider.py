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
from collections import defaultdict
from collections import Counter

def count(sentances):
	result = defaultdict(Counter)
	for sentance in sentances:
		info = test.get_words_info(sentance)
		for i in info:
			# pdb.set_trace()
			result[i[0]][i[3]] += 1
	return result

with open(sys.argv[1]) as f:
	lines = f.readlines()
res = count(lines)
pp = pprint.PrettyPrinter(indent=4)
pp.pprint(res)