from collections import Counter
import CMUTweetTagger as CMU
import test
import sys
from nltk.tokenize import sent_tokenize
from numpy.random import choice
import string
import re
from syllable_count_divider import rhyme_to_POS
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
	# print(rules)
	return rules


def generate_firsttwo(tag_table, pos_syls):
	tag = "Start"
	sentence = ""
	syllable_count = 0
	deadlist_tag = []
	deadlist_syl = []
	end = False
	rhyme_1 = ''
	rhyme_2 = 	''
	while tag != "end":
		cur_syl_count = syllable_count
		next_tag = choice(list(rules[tag].keys()),1,list(rules[tag].values()))[0]
		if next_tag == "end":
			next_tag = "Start"
			continue
		words_info = test.get_words_info(sentence)
		if (syllable_count >= 10 and end):
			rhyme_2 = words_info[len(words_info) - 1][1]
			break
		if (syllable_count == 10):
			rhyme_1 = words_info[len(words_info) - 1][1]
			sentence += "\n"
			syllable_count = 0
			end = True
			continue

		#generate word from tag
		table_by_tag = [k for k in pos_syls[next_tag].keys() if k <= (10 - syllable_count)]
		tries_with_prev_tag = 0
		possible_tries_prev_tag = len(pos_syls)
		if not table_by_tag:
			deadlist_tag.append(next_tag)
			tries_with_prev_tag += 1
			if (tries_with_prev_tag > possible_tries_prev_tag):
				raise Exception("The corpus provided is not big enough")
			continue


		num_syls = choice(table_by_tag, 1)[0]
		word = choice(pos_syls[next_tag][num_syls], 1)[0]
		cur_syl_count += test.get_words_info(word)[0][0]

		if not re.search("[aeiou]", str(word)) :
			continue
		table = str.maketrans({key: None for key in string.punctuation})
		word = str(word).translate(table)  
		if not word:
			continue
		# ##check syllable count
		# words_info = test.get_words_info(sentence + " " + word)

		tries_with_syl_count = 0
		possible_tries_syl = len(pos_syls[next_tag][num_syls])

		tries_with_tag = 0
		possible_tries_tag = len(pos_syls[next_tag])

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
		deadlist_syl = []
		deadlist_tag = []
		tag = next_tag
	return (sentence, rhyme_1, rhyme_2)

def generate_lasttwo(tag_table, pos_syls, rhyme_pos_syls, rhyme1, rhyme2):
	tag = "Start"
	sentence = ""
	syllable_count = 0
	deadlist_tag = []
	deadlist_syl = []
	deadlist_rhyming = []
	end = False
	cur_rhyme = rhyme1
	pos_syls_backup = pos_syls
	while tag != "end":
		cur_syl_count = syllable_count
		next_tag = choice(list(rules[tag].keys()),1,list(rules[tag].values()))[0]
		if next_tag == "end":
			next_tag = "Start"
			continue
		if (syllable_count >= 10 and end):
			# rhyme_2 = words_info[len(words_info) - 1][1]
			break
		if (syllable_count == 10):
			cur_rhyme = rhyme2
			sentence += "\n"
			syllable_count = 0
			end = True
			continue

		#generate word from tag
		table_by_tag = [k for k in pos_syls[next_tag].keys() if k <= (10 - syllable_count)]
		rhyme_POS = rhyme_pos_syls[cur_rhyme]
		# newly added
		table_by_tag_rhyme = [k for k in rhyme_POS[next_tag].keys() if k == (10 - syllable_count)]
		if table_by_tag_rhyme:
			table_by_tag = table_by_tag_rhyme
			pos_syls = rhyme_POS
		tries_with_prev_tag = 0
		possible_tries_prev_tag = len(pos_syls)
		if not table_by_tag:
			deadlist_tag.append(next_tag)
			tries_with_prev_tag += 1
			if (tries_with_prev_tag > possible_tries_prev_tag):
				raise Exception("The corpus provided is not big enough")
			continue


		num_syls = choice(table_by_tag, 1)[0]
		word = choice(pos_syls[next_tag][num_syls], 1)[0]
		cur_word_info = test.get_words_info(word)
		cur_syl_count += cur_word_info[0][0]
		if (cur_syl_count == 10):
			if cur_word_info[0][1] != cur_rhyme:
				try:
					word = choice(rhyme_pos_syls[cur][next_tag][num_syls])[0]
				except:
					deadlist_rhyming.append(next_tag)
					next_tag = tag
					cur_syl_count -= cur_word_info[0][0]
					continue

		if not re.search("[aeiou]", str(word)) :
			continue
		table = str.maketrans({key: None for key in string.punctuation})
		word = str(word).translate(table)  
		if not word:
			continue 
		# ##check syllable count
		# words_info = test.get_words_info(sentence + " " + word)

		tries_with_syl_count = 0
		possible_tries_syl = len(pos_syls[next_tag][num_syls])

		tries_with_tag = 0
		possible_tries_tag = len(pos_syls[next_tag])

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
		deadlist_syl = []
		deadlist_tag = []
		deadlist_rhyming = []
		tag = next_tag
		pos_syls = pos_syls_backup
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

file = open(sys.argv[1], 'r')
count = 0
x = CMU.runtagger_parse(sent_tokenize(file.read())) ##we should strip the sentences of punctuation after the file has been split into sentences
rules = create_rules(x)
tag_table = get_tag_frequencies(x)
syl_rules = get_pos_syllables(x)
rhyme_pos_table = rhyme_to_POS(x)
result1 = generate_firsttwo(rules, syl_rules)
r1 = result1[1]
r2 = result1[2]
firsttwo = result1[0]
result2 = generate_lasttwo(rules, syl_rules, rhyme_pos_table, r1, r2)
lasttwo = result2
print(firsttwo)
print(lasttwo)
# pdb.set_trace()
print()
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