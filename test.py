import subprocess
import unicodedata
import SpecialCharacters
import pdb
from collections import deque

def get_pronunciation(sentence):
    output = subprocess.check_output(['espeak', '-x', '-q', sentence])
    return output

query = input("Enter word: ")

pronunciation = get_pronunciation(query)
list_proc = pronunciation.split()

for term in list_proc:
    print(term)
    term = str(term)
    term = term.rstrip("\"")
    term = term.lstrip("b\"")  
    syl_count = 0
    rhyme_fam = ''
    prev_c = ''
    for c in term:
        c = str(c)
        if c not in SpecialCharacters.vowels:
            rhyme_fam += c
            prev_c = c
        else:
            if prev_c  == '' or prev_c not in SpecialCharacters.vowels:
                syl_count += 1
                rhyme_fam = c
                prev_c = c
            else:
                rhyme_fam += c
                prev_c = c

    print("syllable count " + str(syl_count)),
    print("rhyme: " + rhyme_fam)

