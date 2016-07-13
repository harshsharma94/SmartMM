from __future__ import absolute_import
from __future__ import print_function
import re
import operator
import six
from six.moves import range
from utilities import load_data,cross_validate
from sklearn.pipeline import Pipeline
from keyword_metrics import keyword_prf
from nltk.stem import PorterStemmer
import gensim


class Rake_KeywordSelection(object):
    def __init__(self, stop_words_path, min_char_length=1, max_words_length=5, min_keyword_frequency=1, num_keywords=10,to_stem=False):
        self.__stop_words_path = stop_words_path
        self.__stop_words_pattern = self.build_stop_word_regex(stop_words_path)
        self.__min_char_length = min_char_length
        self.__max_words_length = max_words_length
        self.__min_keyword_frequency = min_keyword_frequency
        self.num_keywords = num_keywords

    def fit(self,X,y=None):
        return self

    def predict(self, X):
        y_pred = []
        keyword_candidates_lst = []
        keyword_candidates_scores_lst = []
        for text in X:
            sentence_list = self.split_sentences(text)
            phrase_list = self.generate_candidate_keywords(sentence_list, self.__stop_words_pattern, self.__min_char_length, self.__max_words_length)
            word_scores = self.calculate_word_scores(phrase_list)
            keyword_candidates = self.generate_candidate_keyword_scores(phrase_list, word_scores, self.__min_keyword_frequency)
            keyword_candidates_lst.append([keyword for (keyword,score) in keyword_candidates.iteritems()])
            keyword_candidates_scores_lst.append(keyword_candidates)
        corpus_tfidf,dictionary = self.score_keyphrases_by_tfidf(keyword_candidates_lst)
        inv_dict = {val : key for key,val in dictionary.iteritems()}
        for idx,keyword_cand_score_pairs in enumerate(keyword_candidates_scores_lst):
            tfidf_keyvals = {tf_id : tf_score for tf_id,tf_score in corpus_tfidf[idx]}
            keywords_available = [dictionary[tf_id] for tf_id in tfidf_keyvals.keys()]
            for keyword in keyword_cand_score_pairs.keys():
                if keyword in keywords_available:
                    keyword_cand_score_pairs[keyword] *= tfidf_keyvals[inv_dict[keyword]]
                else:
                    keyword_cand_score_pairs[keyword] *= 0
            sorted_keywords = sorted(six.iteritems(keyword_cand_score_pairs), key=operator.itemgetter(1), reverse=True)[:self.num_keywords]
            y_pred.append([keyword for keyword,score in sorted_keywords])
        return y_pred

    def score_keyphrases_by_tfidf(self, candidates):
        # make gensim dictionary and corpus
        dictionary = gensim.corpora.Dictionary(candidates)
        corpus = [dictionary.doc2bow(candidate) for candidate in candidates]
        # transform corpus with tf*idf model
        tfidf = gensim.models.TfidfModel(corpus)
        corpus_tfidf = tfidf[corpus]
        return corpus_tfidf, dictionary

    def is_number(self,s):
        try:
            float(s) if '.' in s else int(s)
            return True
        except ValueError:
            return False


    def load_stop_words(self,stop_word_file):
        """
        Utility function to load stop words from a file and return as a list of words
        @param stop_word_file Path and file name of a file containing stop words.
        @return list A list of stop words.
        """
        stop_words = []
        for line in open(stop_word_file):
            if line.strip()[0:1] != "#":
                for word in line.split():  # in case more than one per line
                    stop_words.append(word)
        return stop_words


    def separate_words(self,text, min_word_return_size):
        """
        Utility function to return a list of all words that are have a length greater than a specified number of characters.
        @param text The text that must be split in to words.
        @param min_word_return_size The minimum no of characters a word must have to be included.
        """
        splitter = re.compile('[^a-zA-Z0-9_\\+\\-/]')
        words = []
        for single_word in splitter.split(text):
            current_word = single_word.strip().lower()
            #leave numbers in phrase, but don't count as words, since they tend to invalidate scores of their phrases
            if len(current_word) > min_word_return_size and current_word != '' and not self.is_number(current_word):
                words.append(current_word)
        return words


    def split_sentences(self,text):
        """
        Utility function to return a list of sentences.
        @param text The text that must be split in to sentences.
        """
        sentence_delimiters = re.compile(u'[\\[\\]\n.!?,;:\t\\-\\"\\(\\)\\\'\u2019\u2013]')
        sentences = sentence_delimiters.split(text)
        return sentences


    def build_stop_word_regex(self,stop_word_file_path):
        stop_word_list = self.load_stop_words(stop_word_file_path)
        stop_word_regex_list = []
        for word in stop_word_list:
            word_regex = '\\b' + word + '\\b'
            stop_word_regex_list.append(word_regex)
        stop_word_pattern = re.compile('|'.join(stop_word_regex_list), re.IGNORECASE)
        return stop_word_pattern


    def generate_candidate_keywords(self,sentence_list, stopword_pattern, min_char_length=1, max_words_length=5):
        phrase_list = []
        for s in sentence_list:
            tmp = re.sub(stopword_pattern, '|', s.strip())
            phrases = tmp.split("|")
            for phrase in phrases:
                phrase = phrase.strip().lower()
                if phrase != "" and self.is_acceptable(phrase, min_char_length, max_words_length):
                    phrase_list.append(phrase)
        return phrase_list


    def is_acceptable(self,phrase, min_char_length, max_words_length):

        # a phrase must have a min length in characters
        if len(phrase) < min_char_length:
            return 0

        # a phrase must have a max number of words
        words = phrase.split()
        if len(words) > max_words_length:
            return 0

        digits = 0
        alpha = 0
        for i in range(0, len(phrase)):
            if phrase[i].isdigit():
                digits += 1
            elif phrase[i].isalpha():
                alpha += 1

        # a phrase must have at least one alpha character
        if alpha == 0:
            return 0

        # a phrase must have more alpha than digits characters
        if digits > alpha:
            return 0
        return 1


    def calculate_word_scores(self,phraseList):
        word_frequency = {}
        word_degree = {}
        for phrase in phraseList:
            word_list = self.separate_words(phrase, 0)
            word_list_length = len(word_list)
            word_list_degree = word_list_length - 1
            #if word_list_degree > 3: word_list_degree = 3 #exp.
            for word in word_list:
                word_frequency.setdefault(word, 0)
                word_frequency[word] += 1
                word_degree.setdefault(word, 0)
                word_degree[word] += word_list_degree  #orig.
                #word_degree[word] += 1/(word_list_length*1.0) #exp.
        for item in word_frequency:
            word_degree[item] = word_degree[item] + word_frequency[item]

        # Calculate Word scores = deg(w)/frew(w)
        word_score = {}
        for item in word_frequency:
            word_score.setdefault(item, 0)
            word_score[item] = word_degree[item] / (word_frequency[item] * 1.0)  #orig.
        #word_score[item] = word_frequency[item]/(word_degree[item] * 1.0) #exp.
        return word_score


    def generate_candidate_keyword_scores(self,phrase_list, word_score, min_keyword_frequency=1):
        keyword_candidates = {}

        for phrase in phrase_list:
            if min_keyword_frequency > 1:
                if phrase_list.count(phrase) < min_keyword_frequency:
                    continue
            keyword_candidates.setdefault(phrase, 0)
            word_list = self.separate_words(phrase, 0)
            candidate_score = 0
            for word in word_list:
                candidate_score += word_score[word]
            keyword_candidates[phrase] = candidate_score
        return keyword_candidates



if __name__ == '__main__':
    ids,docs,keywords_doc = load_data()
    # ids = ids[:10]
    # docs = docs[:10]
    # keywords_doc = keywords_doc[:10]
    to_stem=False
    pipeline = Pipeline([
        ('keyword_selector',Rake_KeywordSelection("SmartStoplist.txt",5,3,4,num_keywords=10,to_stem=to_stem))
    ])
    # pipeline.fit(docs)
    # print(pipeline.predict(docs))
    cross_validate((docs,keywords_doc),pipeline,keyword_prf,stem_y=to_stem)

    # def predict(self, X):
    #     y_pred = []
    #     for text in X:
    #         sentence_list = self.split_sentences(text)
    #
    #         phrase_list = self.generate_candidate_keywords(sentence_list, self.__stop_words_pattern, self.__min_char_length, self.__max_words_length)
    #
    #         word_scores = self.calculate_word_scores(phrase_list)
    #
    #         keyword_candidates = self.generate_candidate_keyword_scores(phrase_list, word_scores, self.__min_keyword_frequency)
    #
    #         sorted_keywords = sorted(six.iteritems(keyword_candidates), key=operator.itemgetter(1), reverse=True)
    #         if to_stem:
    #             top_keywords = []
    #             stemmer = PorterStemmer()
    #             for keyword,score in sorted_keywords:
    #                 if len(top_keywords) == self.num_keywords:
    #                     y_pred.append(top_keywords)
    #                     break
    #                 try:
    #                     stemmed_keyword = ' '.join([str(stemmer.stem(word)) for word in keyword.split()])
    #                 except:
    #                     stemmed_keyword = keyword
    #                 if stemmed_keyword not in top_keywords:
    #                     top_keywords.append(stemmed_keyword)
    #         else:
    #             y_pred.append([keyword for (keyword,score) in sorted_keywords[:self.num_keywords]])
    #     return y_pred
