from TwitterSearch import *  #code from https://github.com/ckoepp/TwitterSearch
import test
import subprocess
import unicodedata
import SpecialCharacters
import pdb
import pprint
import CMUTweetTagger as CMU
import re


#Takes a query as an input and searches for tweets related to that query
def getTweets(query):
    pp = pprint.PrettyPrinter(indent=4)
    try:
        tso = TwitterSearchOrder() # create a TwitterSearchOrder object
        print(query)
        tso.set_keywords([query]) # let's define all words we would like to have a look for
        tso.set_language('en') # we want to see English tweets only
        tso.set_include_entities(False) # and don't give us all those entity information   #from original code, idk what it does

        #my API data. 
        ts = TwitterSearch(
            consumer_key = 'CEBkHI0NJWisF9Wh6bo59WilM',
            consumer_secret = 'bYg84yGtUW44IWDCyI2h2ydfArj40aMI0rtPMIhK3uf6vNxEbA',
            access_token = '760218193587732480-5kf55wKpIi05RvUqRGmL0JVOb7txh0b',
            access_token_secret = 'kIEdUMKMuck51cmfbWSIoVIWNeenicMhiW4XMrb8XuChW'
         )

         
         
        count = 1 #how many tweets we want to see
        i = 0 
        for tweet in ts.search_tweets_iterable(tso):
            if i >= count:
                break #stops getting tweets when we have enough
            
            #keep this line below as a reference. from the original code:
            #print( '@%s tweeted: %s' % ( tweet['user']['screen_name'], tweet['text'] ) )

            words = tweet['text']
            start = re.search("(((RT )?@(\w)*) ?:? )?", words)
            pdb.set_trace() 
            words = words.lstrip(start.group(0))
            #don't need a regular expression for URLs, we can delete those with runtagger_parse
            print(words)
            words_info = test.get_words_info(words)
            # pdb.set_trace()
            tags = CMU.runtagger_parse([words])
            pp.pprint(words_info)
            pp.pprint(tags)
                # pronunciation = get_pronunciation("\""+ str(text) +"\"")
            # for term in pronunciation.split(): #takes individual word pronunciations
            #     syllable_count, syllable_list = tokenize(term)
            #     print(term)
            #     syl_count = 0
            #     rhyme_fam = ''
            #     for c in term:
            #         if c not in SpecialCharacters.vowels:
            #             rhyme_fam += str(c)
            #         else:
            #             syl_count += 1
            #             rhyme_fam = str(c)
            #             while next(term) in SpecialCharacters.vowels and t.next is not None:
            #                 c = next(term)
            #                 rhyme_fam += c
            #     print("syllable count " + str(syl_count)),
            #     print("rhyme: " + rhyme_fam)
            i+=1
            
    except TwitterSearchException as e: # take care of all those ugly errors if there are some
        print(e)

#pipes tweet to espeak to obtain phonetic transcription
def get_pronunciation(sentence):
    output = subprocess.check_output(['espeak', '-x', '-q', sentence])
    return output

#tweets contain some special unicode symbols that espeak cannot recognize
def to_ascii(text):
    return unicodedata.normalize('NFKD', text).encode('ascii','ignore')


#this counts the syllables of the pronuncuation and splits it into
#"tokens" The last token is supposed to be the 'rhyme group'. Syllables
#works decently. They rhyme groups is far from perfectm, but it yields results.
def tokenize(term):
    consonants = SpecialCharacters.consonants #list of consonants, not espeak consonants
    vowels = SpecialCharacters.vowels #list of vowels including espeak special vowels
    consonantList = [] #consonants in term
    vowelList = [] #vowels in term
    temp = term 
    for char in term: #replaces all consonants with white space. stores them in a list
        if char in consonants:
            consonantList.append(char)
            term = term.replace(char," ")
    vowelList = term.split()  #splits by white space and obtains all vowels and vowel groups
    syllableCount = len(vowelList) # num vowel groups ~= num syllables
    term = temp
    tokens = [] #list of tokens
    token = "" #current token
    for char in term:
        if char in consonants: #iterates through term. if character is consonant, add to token
            token += char
            #term.replace(char,"",1)
        if char in vowels:
            if token.endswith(char): #if token ends with char, skip char and do not add another vowel group
                    continue
            if token != "": #each token should start with a vowel group if it is not the first token in the term
                tokens.append(token) 
                token = ""
            if len(vowelList) > 0:
                token += vowelList[0]
                del vowelList[0] #pops next vowel group
    if token != "": #add last token
        tokens.append(token)
    return syllableCount,tokens
            
            
                
    

query = input("What do you want to search for? ")
getTweets(query)