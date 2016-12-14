import nltk
from nltk.tokenize import sent_tokenize
import Rules
import random
import sys
import math
from numpy.random import choice


if len(sys.argv) == 1:
	print("Input the name of the file you want to process! ie: 'InterviewTranscript.txt'")	
	exit()

corpus = open(sys.argv[1], 'r')
rules, vocab, num_rules = Rules.get_data(sent_tokenize(corpus.read()))
#print(rules)
#print(vocab)

corpus.close()


sentence = ""
start = rules["S"]
tag = ""
taglist = ""

for i in range(10):
	while tag is not "end": 
		tag = choice(list(start.keys()),1,list(start.values()))[0]#random.choice(list(start.keys())
		if tag == "end":
			break
		# if start[tag] < 10/num_rules:
		# 	continue
		start = rules[tag]
		taglist += tag + " "
		word = choice(list(vocab[tag].keys()),1,list(vocab[tag].values()))[0]
		sentence += word + " "
		# if len(sentence.split()) > 15: #arbitrary break point for sentence length
		#  	break

	print(taglist)
	print(sentence)
	taglist = ""
	sentence = ""
	tag = ""
	start = rules["S"]