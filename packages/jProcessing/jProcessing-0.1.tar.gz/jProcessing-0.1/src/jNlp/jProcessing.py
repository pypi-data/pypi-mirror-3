#!/usr/bin/env python
# -*- coding: utf-8 -*-
from jNlp.jTokenize import jTokenize
def long_substr(str1, str2):
    data = [str1, str2]
    substr = ''
    if len(data) > 1 and len(data[0]) > 0:
        for i in range(len(data[0])):
            for j in range(len(data[0])-i+1):
                if j > len(substr) and all(data[0][i:i+j] in x for x in data):
                    substr = data[0][i:i+j]
    return substr.strip()

class Similarities(object):
    def minhash(self, *args):
        """
        :*args: tokenized string like a nd b
        :Sentences: should be tokenized in string
        a = u"これ はな ん です"
        b = u"かこ れ何 です"
        """
        score = 0.0
        tok_sent_1 = args[0]
        tok_sent_2 = args[1]
        shingles = lambda s: set(s[i:i+3] for i in range(len(s)-2))
        try:
            jaccard_distance = lambda seta, setb: len(seta & setb)/float(len(seta | setb))
            score = jaccard_distance(shingles(tok_sent_1), shingles(tok_sent_2))
            return score
        except ZeroDivisionError: return score

if __name__ == '__main__':
    a = 'Once upon a time in Italy'
    b = 'Thre was a time in America'
    print long_substr(a, b)
    a = u'これでアナタも冷え知らず'
    b = u'これでア冷え知らずナタも'
    print long_substr(a, b).encode('utf-8')
    similarity = Similarities()
    print similarity.minhash(' '.join(jTokenize(a)), ' '.join(jTokenize(b)))




    

