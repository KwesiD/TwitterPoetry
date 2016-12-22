from collections import Counter
import CMUTweetTagger as CMU
import test
import sys
from nltk.tokenize import sent_tokenize
from numpy.random import choice
from numpy import array
import string
import re
from syllable_count_divider import rhyme_to_POS
import copy
import os

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
			if (tag == "U"):
				continue
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
	# print(rules)
	return rules


def generate_firsttwo(tag_table, pos_syls):
	tag = "Start"
	prev_tag = ""
	rules = copy.copy(tag_table)
	sentence = ""
	syllable_count = 0
	# we dont want any emoticons, this also picks up unicode
	deadlist_tag = ["E", ","]
	deadlist_syl = []
	second_line = False
	rhyme_1 = ''
	rhyme_2 = ''
	tries_with_prev_tag = 0
	tries_with_tag = 0
	tries_with_syl_count = 0
	# the base is that we keep generating until we reach the 
	# end of a sentence, instead we need to keep generating
	# until we reach 10 syllables, as outlines in the code below
	while tag != "end":
		cur_syl_count = syllable_count
		if not rules[tag]:
			if prev_tag == "":
				print("Sorry! The search did not provide enough results. Try another!")
				os._exit(1)
			tag = choice(list(rules[prev_tag].keys()),1,list(rules[prev_tag].values()))[0]
		next_tag = choice(list(rules[tag].keys()),1,list(rules[tag].values()))[0]
		if next_tag == "end":
			next_tag = "Start"
			continue
		if next_tag in deadlist_tag:
			if next_tag in rules[tag]:
				del rules[tag][next_tag]
			continue
		words_info = test.get_words_info(sentence)
		# if we are at the second line and have reached 10
		# syllables once again, break out of the loop
		if (syllable_count >= 10 and second_line):
			rhyme_2 = words_info[len(words_info) - 1][1]
			break
		# once we reach 10 syllables the first time, we continue
		# normally so that we can generate 10 more for the second
		# line. the boolean value second_line does this for us
		if (syllable_count == 10):
			rhyme_1 = words_info[len(words_info) - 1][1]
			sentence += "\n"
			syllable_count = 0
			second_line = True
			continue

		# table_by_tag is simply a list of all valid syllable counts
		# for next_tag
		table_by_tag = [k for k in pos_syls[next_tag].keys() if k <= (10 - syllable_count) and k not in deadlist_syl]
		possible_tries_prev_tag = len(pos_syls)
		# if there are no valid counts, try another tag
		if not table_by_tag:
			deadlist_tag.append(next_tag)
			tries_with_prev_tag += 1
			# if we have exhausted all possible tag choices, our 
			# corpus is not large enough
			if (tries_with_prev_tag > possible_tries_prev_tag):
				raise Exception("The corpus provided is not big enough")
			continue

		# randomly choose a number of syllables
		num_syls = choice(table_by_tag, 1)[0]
		# randomly choose a word from the sublist with
		# the number of syllables

		possible_tries_syl = len(pos_syls[next_tag][num_syls])

		possible_tries_tag = len(pos_syls[next_tag])
		if not pos_syls[next_tag][num_syls]:
			deadlist_syl.append(num_syls)
			continue
		word = choice(pos_syls[next_tag][num_syls], 1)[0]
		cur_syl_count += test.get_words_info(word)[0][0]

		# if the word is contains no vowels, we do not want it
		if not re.search("[aeiou]", str(word)) :
			for i in pos_syls[next_tag][num_syls]:
				if i == word:
					pos_syls[next_tag][num_syls].remove(i)
			continue
		# we want to remove punctuation as well, for accuracy
		table = str.maketrans({key: None for key in string.punctuation})
		word = str(word).translate(table)  
		# if the word is only punctuation go on and generate another word
		if not word:
			continue
		# this is the error correction part of the algorithm
		# essentially, if there are no valid words, regenerate
		# excluding the conditions through which we tried
		# to generate the last word.
		# specific conditions are implied by the use of deadlists,
		# to keep track of what has been tried. If we have exhausted all
		# possible options, the corpus is not big enough
		if (tries_with_syl_count > possible_tries_syl):
			deadlist_syl.append(num_syls)
			table_by_tag = [k for k in pos_syls[next_tag].keys() if k < (10 - syllable_count) and k not in deadlist_syl]
			if table_by_tag:	
				num_syls = choice(table_by_tag, 1)[0]
				possible_tries_syl = len(pos_syls[next_tag][num_syls])
				continue
			tries_with_tag += 1
			tries_with_syl_count = 0
			if (tries_with_tag > possible_tries_tag):
				next_tag = choice(list(rules[tag].keys()),1,list(rules[tag].values()))[0]
				tries_with_tag = 0
				tries_with_syl_count = 0
				possible_tries_tag = len(pos_syls[next_tag])
				tries_with_prev_tag += 1
				if (tries_with_prev_tag > possible_tries_prev_tag):
					raise Exception("The corpus provided is not big enough") 

		word_info = test.get_words_info(word)
		# update the total syllable count if no problems arise
		syllable_count += word_info[0][0]
		sentence += word + " "
		tries_with_prev_tag = 0
		tries_with_tag = 0
		tries_with_syl_count = 0
		deadlist_syl = []
		deadlist_tag = ["E", ","]
		rules = copy.copy(tag_table)
		prev_tag = tag
		tag = next_tag
	return (sentence, rhyme_1, rhyme_2)

# this algorithm is essentially the same as above, with a few
# big differences
def generate_lasttwo(tag_table, pos_syls, rhyme_pos_syls, rhyme1, rhyme2):
	# first, this function takes in three extra arguments:
	# the rhymes we are going to go for, and rhyme_pos_syls
	# rhyme_pos_syls is just a table tthat is very similar to 
	# pos_syls, but sorts by rhyme before sorting by tag
	tag = "Start"
	rules = copy.copy(tag_table)
	sentence = ""
	syllable_count = 0
	deadlist_tag = ["E", ","]
	deadlist_syl = []
	deadlist_rhyming = []
	second_line = False
	tries_with_prev_tag = 0
	tries_with_tag = 0
	tries_with_syl_count = 0
	prev_tag = ""
	# cur_rhyme stores the rhyme we are currently going for, since
	# this will generate 2 lines
	cur_rhyme = rhyme1
	# temporary variable that holds our pos_syls table
	pos_syls_backup = copy.copy(pos_syls)
	while tag != "end":
		cur_syl_count = syllable_count

		if not rules[tag]:
			if prev_tag == "":
				print("Sorry! The search did not provide enough results. Try another!")
				os._exit(1)
		next_tag = choice(list(rules[tag].keys()),1,list(rules[tag].values()))[0]
		if next_tag == "end":
			next_tag = "Start"
			continue
		if next_tag in deadlist_tag:
			if next_tag in rules[tag]:
				del rules[tag][next_tag]
			continue
		if (syllable_count >= 10 and second_line):
			# rhyme_2 = words_info[len(words_info) - 1][1]
			break
		if (syllable_count == 10):
			cur_rhyme = rhyme2
			sentence += "\n"
			syllable_count = 0
			second_line = True
			continue

		#generate word from tag
		table_by_tag = [k for k in pos_syls[next_tag].keys() if k <= (10 - syllable_count) and k not in deadlist_syl]
		rhyme_POS = rhyme_pos_syls[cur_rhyme]
		# newly added. this table_by_tag checks if there are any
		# valid words that rhyme with our current rhyme, we should
		# use them
		table_by_tag_rhyme = [k for k in rhyme_POS[next_tag].keys() if k == (10 - syllable_count)]
		# if there are, we should use them
		if table_by_tag_rhyme:
			# this is effectively making rhyme_POS the basis
			# with which we will select words. rhyme_POS is the
			# same as pos_syls but with our current rhyme words only

			table_by_tag = table_by_tag_rhyme
			pos_syls = rhyme_POS
		possible_tries_prev_tag = len(pos_syls)

		if not table_by_tag:
			deadlist_tag.append(next_tag)
			tries_with_prev_tag += 1
			if (tries_with_prev_tag > possible_tries_prev_tag):
				raise Exception("The corpus provided is not big enough")
			continue


		num_syls = choice(table_by_tag, 1)[0]

		possible_tries_syl = len(pos_syls[next_tag][num_syls])

		possible_tries_tag = len(pos_syls[next_tag])
		if not pos_syls[next_tag][num_syls]:
			deadlist_syl.append(num_syls)
			continue
		word = choice(pos_syls[next_tag][num_syls], 1)[0]
		cur_word_info = test.get_words_info(word)
		cur_syl_count += cur_word_info[0][0]
		if (cur_syl_count == 10):
			# if we have reached 10 syllables and still have not
			# found a word that rhymes, we need to force
			# our program to find a word that does
			if cur_word_info[0][1] != cur_rhyme:
				# first it will look for one in rhyme_pos_syls
				possible_tries_rhyme = len(rhyme_pos_syls[cur_rhyme])
				try:
					word = choice([rhyme_pos_syls[cur_rhyme][tag][num_syls] for tag in rhyme_pos_syls[cur_rhyme].keys() if tag not in deadlist_rhyming])[0]
				# if none exist, we need to choose another tag that
				# has valid rhymes
				except:
					deadlist_rhyming.append(next_tag)
					if len(deadlist_rhyming) > possible_tries_rhyme:
						print("Sorry! The search did not return enough results. No rhyming words were found!")
						os._exit(1)
					cur_syl_count -= cur_word_info[0][0]
					continue

		if not re.search("[aeiou]", str(word)) :
			for i in pos_syls[next_tag][num_syls]:
				if i == word:
					pos_syls[next_tag][num_syls].remove(i)
			continue
		table = str.maketrans({key: None for key in string.punctuation})
		word = str(word).translate(table)  
		if not word:
			continue 

		if (tries_with_syl_count > possible_tries_syl):
			deadlist_syl.append(num_syls)
			table_by_tag = [k for k in pos_syls[next_tag].keys() if k < (10 - syllable_count) and k not in deadlist_syl]
			if table_by_tag:	
				num_syls = choice(table_by_tag, 1)[0]
				possible_tries_syl = len(pos_syls[next_tag][num_syls])
				continue
			tries_with_tag += 1
			tries_with_syl_count = 0
			if (tries_with_tag > possible_tries_tag):
				next_tag = choice(list(rules[tag].keys()),1,list(rules[tag].values()))[0]
				tries_with_tag = 0
				tries_with_syl_count = 0
				possible_tries_tag = len(pos_syls[next_tag])
				tries_with_prev_tag += 1
				if (tries_with_prev_tag > possible_tries_prev_tag):
					raise Exception("The corpus provided is not big enough") 

		word_info = test.get_words_info(word)
		syllable_count += word_info[0][0]
		sentence += word + " "
		tries_with_prev_tag = 0
		tries_with_tag = 0
		tries_with_syl_count = 0
		deadlist_syl = []
		deadlist_tag = ["E", ","]
		deadlist_rhyming = []
		prev_tag = tag
		tag = next_tag
		# once we are done dealing with a specific rhyme, 
		# we want to be sure that we return pos_syls to normal
		# so we can still generate non-rhyming words. 
		pos_syls = copy.copy(pos_syls_backup)
		rules = copy.copy(tag_table)
	return sentence


def check_seq_word(word_info, prev_stress_OG):
	syllables = word_info[2]
	valid = True 
	prev_stress = prev_stress_OG
	for syl in syllables:
		cur_stress = syl[1]
		if (cur_stress == prev_stress):
			valid = False 
			break
		prev_stress = cur_stress
	last_stress = prev_stress
	return (valid, last_stress)

def iambic_pentameter(words_info):
	prev_stress_OG = False
	for word_info in words_info:
		sequence = check_seq_word(word_info,prev_stress_OG)  
		valid = sequence[0]
		if not valid:
			return False
		prev_stress_OG = sequence[1]
	return True
