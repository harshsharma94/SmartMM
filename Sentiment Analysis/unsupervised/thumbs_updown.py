from __future__ import division
from nltk import wordpunct_tokenize,pos_tag
from nltk.corpus import stopwords
import re
import urllib
import requests
import math
from utilities import load_data
import time
from random import randint
from py_bing_search import PyBingSearch


__author__ = 'tangy'

#TODO: Wikipedia based Sentiment Analysis
# Papers:
# http://www.cs.bris.ac.uk/~flach/ECMLPKDD2012papers/1125567.pdf


class thumbs_updown:

    def __init__(self,search_engine="google"):
        assert search_engine in ["google","bing"], "`search_engine` is either `google`/`bing`"
        self.search_engine = search_engine
        self.hits_poor = self._hits("poor")
        self.hits_excellent = self._hits("excellent")

    def predict(self,X):
        sentence_tokens = self._process(X)
        scorer = []
        for sent in sentence_tokens:
            score = 0
            sent_len = len(sent)
            for token_tuple in sent:
                score += self._get_so(token_tuple[0] + " " + token_tuple[1])
            score_avg = (score/sent_len)
            if score_avg >= 0:
                scorer.append(1)
            else:
                scorer.append(0)
        return scorer


    def _process(self,sentences):
        sentences = map(lambda sentence:re.sub("<br />","",sentence),sentences)
        print sentences
        sentence_tokens = map(lambda sentence: wordpunct_tokenize(sentence.lower()),sentences)
        sentence_tokens_clean = map(lambda sentence: [word for word in sentence if not word in stopwords.words("english")],sentence_tokens)
        sentence_pos = map(lambda sentence_token: pos_tag(sentence_token),sentence_tokens_clean)
        sent_tags = []
        for token_pos in sentence_pos:
            acceptable_tags = []
            for i in xrange(2,len(token_pos)):
                if self.pattern_check((token_pos[i-2][1],token_pos[i-1][1],token_pos[i][1])) is True:
                    acceptable_tags.append((token_pos[i-2][0],token_pos[i-1][0]))
            if len(acceptable_tags) > 0:
                sent_tags.append(acceptable_tags)
        print sent_tags
        return sent_tags

    def pattern_check(self,pos_pattern):
        acceptable_patterns = [
            ('JJ','NN,NNS','*'),
            ('RB,RBR,RBS','JJ','!NN,!NNS'),
            ('JJ','JJ','!NN,!NNS'),
            ('NN,NNS','JJ','!NN,!NNS'),
            ('RB,RBR,RBS','VB,VBD,VBN,VBG','*')
            ]
        for pattern in acceptable_patterns:
            p_flags = [False for i in range(3)]
            for i in range(len(pattern)):
                    ps = pattern[i].split(',')
                    iter = 0
                    for p in ps:
                        if p[0] == '!':
                            if iter == 0:
                                p_flags[i] = True
                            if p[1:] == pos_pattern[i]:
                                p_flags[i] = False & p_flags[i]
                        elif p[0] == '*':
                                p_flags[i] = True
                        else:
                            if p == pos_pattern[i]:
                                p_flags[i] = True | p_flags[i]
                        iter += 1
            p_dec = True
            for p_flag in p_flags:
                p_dec = p_dec & p_flag
            if p_dec == True:
                return True
        return False

    def _hits(self,my_query):
        if self.search_engine == "google":
            query = urllib.urlencode({'q' : my_query})
            time.sleep(randint(0,4))
            r = requests.get('https://www.google.com/search?' + query)
            searchres_param = "id=\"resultStats\">((About |)[0-9,]+) result(|s)</div>"
            print my_query
            try:
                count = re.search(searchres_param,r.text).group(1)
                if "About " in count:
                    count = count.strip("About ")
                print "Result found"
                return (int(str(re.sub(',','',count))) + 0.01)
            except:
                print "No results"
                return 0.01
        elif self.search_engine == "bing":
            bing = PyBingSearch('xAFcyVsidXgkpQxwHYkPcPPPRGpjU2qlNtjBD6ZqGNU')
            result_list,next_url = bing.search(my_query)
            if len(result_list) > 0:
                return len(result_list) + 0.01
            else:
                return 0.01


    def _get_so(self,phrase):
        if self.search_engine == "google":
            op = "AROUND(10)"
        elif self.search_engine == "bing":
            op = "near:10"
        hits_phrase_excellent = self._hits('"%s" %s "excellent"' % (phrase, op))
        hits_phrase_poor = self._hits('"%s" %s "poor"' % (phrase, op))
        so = (hits_phrase_excellent*self.hits_poor)/(hits_phrase_poor*self.hits_poor)
        so_log = math.log(so,2)
        return so_log

if __name__=='__main__':
    ids,X,y = load_data("stanford")
    unsupervised_clf = thumbs_updown(search_engine="bing")
    ypred = unsupervised_clf.predict(X[10:12])
    print X[10:12]
    print ypred
    print y[10:12]



