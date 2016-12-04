import subprocess
import unicodedata
import SpecialCharacters
import pdb
from collections import deque


def get_pronunciation(sentence):
    """
    need espeak installed for this to work, this process returns the 
    pronounciaiton as espeak would return it by running espeak as a
    subprocess.
    """
    output = subprocess.check_output(['espeak', '-x', '-q', sentence])
    return output.decode("utf-8")

query = input("Enter word: ")

skip = ["%", "=", "_", ":", "|"]

pronounciaiton = get_pronunciation(query)
query = query.split()
list_proc = pronounciaiton.split()
i = 0
for term in list_proc:
    print(str(query[i]))
    i += 1
    # for each term provided
    print(term)
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
    term += " "
    for c in term:
        # for each character in the term
        c = str(c)
        pdb.set_trace()
        if c == " ":
            last_syl = True
        cur_syl += c 
        # pdb.set_trace()
        # if the character is not a vowel, we should include it in the rhyme family
        if c in skip:
            continue
        if c in ["\'", ","]:
            cur_stressed = True
            prev_c = "\'"
            continue
        if c not in SpecialCharacters.vowels:
            if first_syl:
                rhyme_fam += c
                prev_c = c
                first_syl = False
            elif prev_c not in SpecialCharacters.vowels:
                rhyme_fam += cur_syl
                prev_c = c
            elif last_syl:
                last = syllables.pop()
                now = (last[0] + cur_syl.strip(), last[1])
                syllables.append(now)
            else:
                syllables.append((cur_syl.rstrip(c), cur_stressed))
                cur_stressed = False
                rhyme_fam += c
                cur_syl = c
        # if the character is a vowel, we run into several possible situations
        else:
            # if we start a new word or the previous character is not a vowel,
            # we have started a new syllable and its time to reset
            if prev_c == '':
                prev_c = c
                first_syl = False
                continue
            elif prev_c not in SpecialCharacters.vowels:
                rhyme_fam = c
                prev_c = c
            # otherwise the character is a part of the current rhyme family 
            elif c == " ":
                continue
            else: 
                rhyme_fam += c
                prev_c = c
        syl_count=  len(syllables)
    
    pdb.set_trace()
    syllables.append((cur_syl, cur_stressed))
    cur_stressed = False
    print("syllable count " + str(syl_count)),
    print("rhyme: " + rhyme_fam)
