import nltk
import sys
import math
import re

#tags a corpus using NLTK. The corpus should have each sentence on a single line for now
def tag(corpus):
	tags = "" #Document converted to tags
	punctuation = [":",",",".","(",")","\'","\""," ","\"\"","\'\'","\'","$","``"] #punctuation to omit
	vocab = {}
	#vocab_counts = {}

	for sentence in corpus: 
		text = nltk.word_tokenize(sentence)
		line = "S " #S is for Start, not the POS tag for Sentence
		tagged_sentence = nltk.pos_tag(text)
		for pair in tagged_sentence: #pair is the word and its tag
			tag = pair[1]
			word = pair[0]
			if tag in punctuation:
				continue
			line += tag + " "
			if tag in vocab:
				if word not in vocab[tag]:
					vocab[tag][word] = 1
					#vocab_counts[tag][word] = 1
				else:
					vocab[tag][word] += 1
					#vocab_counts[tag][word] = 1
			else:
				vocab[tag] = {word:1}
				#vocab_counts[tag] = {word:1}
			
		line = line.strip()
		line += "\n" 
		tags += line #adds the line of tags
	# for tag in vocab:
	# 	for word in vocab[tag]:
	# 		print(word + " " + str(vocab[tag][word]))
	return tags,vocab #,vocab_counts





#Generates the bigrams from the tags
def create_rules(tags):
	num_rules = 0
	rules = {}
	rule_counts = {}
	for line in tags.strip().split("\n"):
		prev = ""
		for tag in line.strip().split():
			if prev == "":
				prev = tag
			else:
				if prev in rules:
					if tag in rules[prev]:
						rules[prev][tag] += 1 
						rule_counts[prev][tag] += 1
					else:
						rules[prev][tag] = 1
						rule_counts[prev][tag] = 1

				else:
					rules[prev] = {}
					rule_counts[prev] = {}
					rules[prev][tag] = 1
					rule_counts[prev][tag] = 1
				num_rules += 1
				prev = tag
		if prev not in rules:
			rules[prev] = {}
			rule_counts[prev] = {}
		if "end" in rules[prev]:
			rules[prev]["end"] += 1
			rule_counts[prev]["end"] += 1
		else:
			rules[prev]["end"] = 1
			rule_counts[prev]["end"] = 1
		num_rules += 1
	return rules, num_rules#rule_counts, num_rules



def get_rule_frequencies(rules):#,rule_counts):
	for  t1 in rules:
		for t2 in rules[t1]:
			rules[t1][t2] /= sum(list(rules[t1].values()))#sum(list(rule_counts[t1].values()))
			print(t1 + " -> " + t2 + ": " + str(rules[t1][t2]))
	return rules

def get_vocab_frequencies(vocab):#,#vocab_counts):
	for tag in vocab:
		total = sum(list(vocab[tag].values()))
		for term in vocab[tag]:
			vocab[tag][term] /= total
	return vocab

#grabs all the data from the corpus such as words,tags, bigrams and frequencies
def get_data(corpus):
	tags, vocab = tag(corpus) #vocab_counts = tag(corpus)
	rules,num_rules = create_rules(tags)#rules,rule_counts, num_rules = create_rules(tags)
	rules = get_rule_frequencies(rules)#,rule_counts)
	vocab = get_vocab_frequencies(vocab)
	output = open("rules.txt",'w')
	for t1 in rules:
		for t2 in rules[t1]:
			output.write(t1 + " -> " + t2 + " : " + str(rules[t1][t2]) + '\n')
	output.close()
	return rules, vocab, num_rules

# if len(sys.argv) == 1:
# 	print("Input the name of the file you want to process! ie: 'InterviewTranscript.txt'")	
# 	exit()

# corpus = open(sys.argv[1], 'r')
# tags = tag(corpus)
# corpus.close()
# #print(tags)
# rules,num_rules = create_rules(tags)
# rules = get_frequencies(rules,num_rules)
# output = open("rules.txt",'w')
# x = 0
# for t1 in rules:
# 	for t2 in rules[t1]:
# 		output.write(t1 + " -> " + t2 + " : " + str(rules[t1][t2]) + '\n')
# 		x += rules[t1][t2]
# print("Number of rules = " + str(num_rules))
# print("Total = " + str(x))
# output.close()