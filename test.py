import subprocess
import unicodedata
import SpecialCharacters
import pdb
from collections import deque
import pprint


word_info_table = {}

def get_pronunciation(sentence):
    """
    need espeak installed for this to work, this process returns the 
    pronounciaiton as espeak would return it by running espeak as a
    subprocess.
    """
    output = subprocess.check_output(['espeak', '-x', '-q', sentence.strip('-')])
    return output.decode("utf-8")


def get_words_info(words):

    query = words

    skip = ["%", "=", "_", ":", "|"]

    results = []

    query = query.split()
    #pronounciaiton = [(k, get_pronunciation(k)) for k in query]
    pronounciaiton = []
    for term in query:
        if term in word_info_table:
            pronounciaiton.append((term,"Already Exists"))
        else:
            pronounciaiton.append((term,get_pronunciation(term)))

    list_proc = pronounciaiton
    i = -1
    for term in list_proc:
        # print(str(query[i]))
        if term[1] == "Already Exists":
            results.append(word_info_table[term[0]])
            continue
        cur_word = term[0]
        term = term[1]
        i += 1
        # for each term provided
        # print(term)
        syl_count = 0
        # we contruct the rhyme family by figuing out the current syllable,
        # the last syllable in the word is the rhyme family
        rhyme_fam = ''
        # we need the previous character to realize if we have reached a new
        # syllable or not.
        prev_c = ''
        syllables = []
        cur_stressed = False
        first_syl = True
        last_syl = False
        cur_syl = ''
        term = term.strip()
        term += "*"
        for c in term:
            # for each character in the term
            c = str(c)

            if c == "*":
                contains = False
                if not first_syl:
                    for v in SpecialCharacters.vowels:
                        if v in cur_syl:
                            contains = True
                            break
                if not contains:
                    first_syl = True
                last_syl = True
            cur_syl += c 

            # if the character is not a vowel, we should include it in the rhyme family
            if c in skip:
                continue
            if c in ["\'", ","]:
                cur_stressed = True
                prev_c = "\'"
                continue
            if c in SpecialCharacters.vowels and first_syl and last_syl:
                if prev_c not in SpecialCharacters.vowels:
                    syl = syllables.pop()
                    last = syl[0]
                    syllables.append((last, cur_stressed))
                    break
                else:
                    syllables.append((cur_syl.strip(), cur_stressed))
            if c not in SpecialCharacters.vowels:
                if last_syl and first_syl:
                    if syllables:
                        syl = syllables.pop()
                        last = syl[0]
                        last_stressed = syl[1]
                        syllables.append((last, last_stressed))
                    else:
                        last = cur_syl.strip("*")
                        syllables.append((last, cur_stressed))
                    break
                elif last_syl:
                    # last = syllables.pop()
                    # now = (last[0] + cur_syl.strip(), last[1])
                    # pdb.set_trace()
                    syllables.append((cur_syl.strip(), cur_stressed))
                elif prev_c not in SpecialCharacters.vowels:
                    rhyme_fam += c 
                    prev_c = c
                else:
                    if (c == "*"):
                        syllables.append((cur_syl.rstrip(c), cur_stressed))
                    else:
                        syllables.append((cur_syl, cur_stressed))
                    cur_stressed = False
                    first_syl = False
                    rhyme_fam += c
                    cur_syl = c
                    prev_c = c
            # if the character is a vowel, we run into several possible situations
            else:
                # if we start a new word or the previous character is not a vowel,
                # we have started a new syllable and its time to reset
                if prev_c == '':
                    prev_c = c
                    first_syl = True
                    rhyme_fam += c
                    continue
                elif prev_c not in SpecialCharacters.vowels:
                    rhyme_fam = c
                    prev_c = c
                # otherwise the character is a part of the current rhyme family 
                elif c == "*":
                    continue
                else: 
                    rhyme_fam += c
                    prev_c = c
        syl_count=  len(syllables)
        cur_stressed = False
        word_info_table[cur_word] = (syl_count, rhyme_fam, syllables, cur_word)
        results.append((syl_count, rhyme_fam, syllables, cur_word))

    return results


