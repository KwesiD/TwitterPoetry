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
    return output

query = input("Enter word: ")

pronunciation = get_pronunciation(query)
list_proc = pronunciation.split()

for term in list_proc:
    # for each term provided
    print(term)
    term = str(term)
    # we dont want the right hanging aposrophe that espeak returns
    term = term.rstrip("\"")
    # or the left b", all we need is the pronounciation
    term = term.lstrip("b\"")  
    syl_count = 0
    # we contruct the rhyme family by figuing out the current syllable,
    # the last syllable in the word is the rhyme family
    rhyme_fam = ''
    # we need the previous character to realize if we have reached a new
    # syllable or not.
    prev_c = ''
    for c in term:
        # for each character in the term
        c = str(c)
        # if the character is not a vowel, we should include it in the rhyme family
        if c not in SpecialCharacters.vowels:
            rhyme_fam += c
            prev_c = c
        # if the character is a vowel, we run into two possible situations
        else:
            # if we start a new word or the previous character is not a vowel,
            # we have started a new syllable and its time to reset
            if prev_c  == '' or prev_c not in SpecialCharacters.vowels:
                syl_count += 1
                rhyme_fam = c
                prev_c = c
            # otherwise the character is a part of the current syllable 
            else: 
                rhyme_fam += c
                prev_c = c

    print("syllable count " + str(syl_count)),
    print("rhyme: " + rhyme_fam)

