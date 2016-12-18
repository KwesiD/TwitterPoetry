from collections import Counter

def get_tag_frequencies(tagged_words):
	tag_table = {}
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