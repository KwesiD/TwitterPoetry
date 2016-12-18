from collections import Counter
import CMUTweetTagger as CMU
import test
import sys
from nltk.tokenize import sent_tokenize
from numpy.random import choice

#takes in a list of sets. Each set contains a list of the words, their tags, and the probabilities
def get_tag_frequencies(tagged_words):
	tag_table = {}
	# for results in tagged_words:
	# 	for sentence in results :
	for group in tagged_words: 
		for word,tag,prob in group:
			if prob <= .65:
				continue
			if tag not in tag_table:
				tag_table[tag] = Counter([word])
			else:
				tag_table[tag][word] += 1
	for tag in tag_table:
		tagset = tag_table[tag]
		total = sum(tagset.values())
		for word in tagset:
			tagset[word] /= total
		return tag_table



def make_rhyme_table(sentence_list):
	rhyme_table = {}
	for sentence in sentence_list:
		word_data = test.get_words_info(sentence)#.replace("&amp","&")
		for data,term in zip(word_data,sentence.split()):
			if data[1] not in rhyme_table:
				#print(sentence.split())
				rhyme_table[data[1]] = {data[0]:[term]} ##rhyme_Table[rhymefam] = {syllable:term}
			else:
				if data[0] not in rhyme_table[data[1]]:
					rhyme_table[data[1]][data[0]] = [term]
				elif term not in rhyme_table[data[1]][data[0]]:
					rhyme_table[data[1]][data[0]].append(term)
		
	# for fam in rhyme_table:
	# 	print(fam,rhyme_table[fam],sep=" : ")
	# print(len(word_data))
	# print(len(sentence.split()))
	# for a,b in zip(word_data,sentence.split()):
	# 	print(a,b,sep = ":")

	return rhyme_table

#pos -> syl -> word
def get_pos_syllables(tagged_words):
	table = {}
	for group in tagged_words:
		for word,tag,prob in group:
			data = test.get_words_info(word)[0]
			if tag not in table:
				table[tag] = {data[0]:[word]}
			elif data[0] not in table[tag]:
				table[tag][data[0]] = [word]
			elif word not in table[tag][data[0]]:
				table[tag][data[0]].append(word)
	return table

#Should take in a set of results from CMU tagger. [[CMU results sentence 1],[Results sentence 2],....]
def create_rules(tags):
	rules = {}
	#rule_counts = {}
	for tagset in tags:
		prev = "Start"
		#tag = ""
		###for group in tagset:
		
		for word,tag,prob in tagset:
			if prev == "Start":
				rules[prev] = Counter([tag])
				prev = tag
			else:
				if prev in rules:
					if tag in rules[prev]:
						rules[prev][tag] += 1
					else:
						rules[prev][tag] = 1 ##sdfghjk
				else:
					rules[prev] = Counter([tag])
			prev = tag
		if prev not in rules:
			rules[prev] = Counter([])
		if "end" in rules[prev]:
			rules[prev]["end"] += 1
		else:
			rules[prev]["end"] = 1
	for tag in rules:
		total = sum(rules[tag].values())
		for value in rules[tag]:
			rules[tag][value] /= total
	print(rules)
	return rules


def generate(rules,tag_table):
	tag = "Start"
	sentence = ""
	syllable_count = 0
	while tag != "end":
		next_tag = choice(list(rules[tag].keys()),1,list(rules[tag].values()))[0]
		if next_tag == "end":
			break
		tag = next_tag
		#generate word from tag
		word = choice(list(tag_table[next_tag].keys()),1,list(tag_table[next_tag].values()))[0]
		##check syllable count
		sentence += word + " "

	print(sentence)

		

file = open(sys.argv[1], 'r')
count = 0
x = CMU.runtagger_parse(sent_tokenize(file.read())) ##we should strip the sentences of punctuation after the file has been split into sentences
rules = create_rules(x)
tag_table = get_tag_frequencies(x)
generate(rules,tag_table)
# for line in file:
# 	sent.append(CMU.runtagger_parse(line))
# 	count += 1
# 	if count >= 3:
# 		break
# create_rules(sent)

	# 	prev = ""
	# 	for tag in line.strip().split():
	# 		if prev == "":
	# 			prev = tag
	# 		else:
	# 			if prev in rules:
	# 				if tag in rules[prev]:
	# 					rules[prev][tag] += 1 
	# 					rule_counts[prev][tag] += 1
	# 				else:
	# 					rules[prev][tag] = 1
	# 					rule_counts[prev][tag] = 1

	# 			else:
	# 				rules[prev] = {}
	# 				rule_counts[prev] = {}
	# 				rules[prev][tag] = 1
	# 				rule_counts[prev][tag] = 1
	# 			num_rules += 1
	# 			prev = tag
	# 	if prev not in rules:
	# 		rules[prev] = {}
	# 		rule_counts[prev] = {}
	# 	if "end" in rules[prev]:
	# 		rules[prev]["end"] += 1
	# 		rule_counts[prev]["end"] += 1
	# 	else:
	# 		rules[prev]["end"] = 1
	# 		rule_counts[prev]["end"] = 1
	# 	num_rules += 1
	# return rules, num_rules#rule_counts, num_rules