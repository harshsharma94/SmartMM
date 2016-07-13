from utilities import CandidateSelection,DataClean
from utilities import load_data,cross_validate
from sklearn.pipeline import Pipeline
from keyword_metrics import keyword_prf,keyword_prf_onegram
from nltk.stem import PorterStemmer
import re
import collections
import nltk
import math
import numpy as np
import itertools
from sklearn import svm
from pprint import pprint

#TODO: Strict keyword checking to form labels or liberal?(currently strict)

class PairwiseRankingSVM(svm.LinearSVC):

    def __init__(self,keyword_count=10,keyword_maxlen=5,stem=True):
        super(PairwiseRankingSVM,self).__init__()
        self.keyword_count = keyword_count
        self.keyword_maxlen = keyword_maxlen
        if stem:
            self.stemmer = PorterStemmer()

    def transform_pairwise(self,X,y):
        """Transforms data into pairs with balanced labels for ranking
        Transforms a n-class ranking problem into a two-class classification
        problem. Subclasses implementing particular strategies for choosing
        pairs should override this method.
        In this method, all pairs are choosen, except for those that have the
        same target value. The output is an array of balanced classes, i.e.
        there are the same number of -1 as +1
        Parameters
        ----------
        X : array, shape (n_samples, n_features)
            The data
        y : array, shape (n_samples,) or (n_samples, 2)
            Target labels. If it's a 2D array, the second column represents
            the grouping of samples, i.e., samples with different groups will
            not be considered.
        Returns
        -------
        X_trans : array, shape (k, n_feaures)
            Data as pairs
        y_trans : array, shape (k,)
            Output class labels, where classes have values {-1, +1}
        """
        X_new = []
        y_new = []
        y = np.asarray(y)
        # Creates all possible combinations of 2 samples without repitition
        comb = itertools.combinations(range(X.shape[0]), 2)
        for k,(i,j) in enumerate(comb):
            if y[i] == y[j]:
                # Skip if combination pair labels are same
                continue
            X_new.append(X[i] - X[j])
            y_new.append(y[i] - y[j])
            # To balance the number of classes 1/-1
            if y_new[-1] != (-1)**k:
                X_new[-1] = X_new[-1] * -1
                y_new[-1] = y_new[-1] * -1
        return np.asarray(X_new),np.asarray(y_new)

    def process_labels(self,candidates,y):
        ymodded = []
        for idx in xrange(len(candidates)):
            candidate_set = candidates[idx]
            keyword_set = y[idx]
            for candidate in candidate_set.keys():
                if candidate in keyword_set:
                    ymodded.append(1)
                else:
                    ymodded.append(0)
        return np.array(ymodded)

    def process_features(self,candidates):
        Xmodded = []
        for idx in xrange(len(candidates)):
            candidate_set = candidates[idx]
            for candidate in candidate_set.keys():
                Xmodded.append(candidate_set[candidate].values())
        return np.array(Xmodded)

    def fit(self,X,y):
        ytf = self.process_labels(X,y)
        Xtf = self.process_features(X)
        Xpairwise,ypairwise = self.transform_pairwise(Xtf,ytf)
        super(PairwiseRankingSVM,self).fit(Xpairwise,ypairwise)
        return self

    def predict(self,X):
        if hasattr(self, 'coef_'):
            ypred = []
            for x in X:
                candidate_keywords = x.keys()
                xtf = self.process_features([x])
                ytf = set()
                keyword_idxes = np.argsort(np.dot(xtf, self.coef_[0].T))[::-1]
                for top_keyword_idx in keyword_idxes.tolist():
                    top_keyword = candidate_keywords[top_keyword_idx]
                    if len(top_keyword.split()) <= self.keyword_maxlen:
                        if hasattr(self, 'stemmer'):
                            top_keyword = ' '.join([self.stemmer.stem(word) for word in top_keyword.split()])
                        ytf.add(top_keyword)
                        if len(ytf) == self.keyword_count:
                            break
                ypred.append(list(ytf))
            return ypred
        else:
            raise ValueError("Must call fit() prior to predict()")

class CandidateFeatureExtractor:

    def __init__(self):
        self.pos_tagger = nltk.tag.PerceptronTagger()
        self.tagset = nltk.load('help/tagsets/upenn_tagset.pickle').keys()


    def extract_features(self,candidate,text,doc_word_counts):
        feature_dict = {}
        pattern = re.compile(r'\b'+re.escape(candidate)+r'(\b|[,;.!?]|\s)', re.IGNORECASE)
        # frequency based
        # # count of candidate in doc
        cand_doc_count = len(pattern.findall(text))
        # # waarn when count is 0
        if cand_doc_count == 0:
            print "Warning : No occurence of candidate %s found in text" % candidate
        feature_dict['candidate_doc_count'] = cand_doc_count

        # statistical
        candidate_words = candidate.split(" ")
        feature_dict['max_word_len'] = max([len(w) for w in candidate_words])
        feature_dict['term_length'] = len(candidate_words)
        sum_doc_word_counts = float(sum(doc_word_counts[w] for w in candidate_words))
        feature_dict['candidate_word_doc_counts_sum'] = sum_doc_word_counts
        try:
            if feature_dict['term_length'] == 1:
                # lexical cohesion doesnt make sense for 1 word terms
                lexical_cohesion = 0.0
            else:
                lexical_cohesion = ( feature_dict['term_length'] *
                                   (1 + math.log(cand_doc_count,10)) *
                                   feature_dict['candidate_doc_count'] ) / sum_doc_word_counts
        except (ValueError,ZeroDivisionError) as e:
            lexical_cohesion = 0.0
        feature_dict['lexical_cohesion'] = lexical_cohesion

        # positional
        # found in title, key excerpt
        split_text = text.split('abstract')
        title = split_text[0]
        excerpt = ' '.join(split_text[1:])
        feature_dict['in_title'] = 1 if pattern.search(title) else 0
        feature_dict['in_excerpt'] = 1 if pattern.search(excerpt) else 0
        # first/last position, difference between them (spread)
        doc_text_length = float(len(text))
        if feature_dict['in_title'] != 0 or feature_dict['in_excerpt'] != 0:
            first_match = pattern.search(text)
            abs_first_occurence = first_match.start()/doc_text_length
            if cand_doc_count == 1:
                spread = 0.0
                abs_last_occurence = abs_first_occurence
            else:
                for last_match in pattern.finditer(text):
                    pass
                abs_last_occurence = last_match.start()/doc_text_length
                spread = abs_last_occurence - abs_first_occurence
            feature_dict['abs_first_occurence'] = abs_first_occurence
            feature_dict['abs_last_occurence'] = abs_last_occurence
            feature_dict['spread'] = spread
        else:
            # print "Candidate %s : not found in text. Skipping this candidate" % candidate
            return -1

        # pos tags - to test
        # def pos_tag_to_id(candidate):
        #     pos_tags = [tag for word,tag in self.pos_tagger.tag(candidate.split())]
        #     assert isinstance(pos_tags,list),"`pos_tags` must be a list"
        #     pos_tag_ids = [str(self.tagset.index(tag) + 1) for tag in pos_tags]
        #     numerical_id = int(''.join(pos_tag_ids))
        #     return numerical_id
        # feature_dict['pos_tag_identifier'] = pos_tag_to_id(candidate)
        return feature_dict

    def fit(self,X,y=None):
        return self

    def transform(self,X):
        candidate_lst = CandidateSelection().fit_transform(X)
        candidate_features_lst = []
        for idx in xrange(len(candidate_lst)):
            print idx
            candidate_features = {}
            text = X[idx]
            doc_word_counts = collections.Counter(word for sent in nltk.sent_tokenize(text)
                                      for word in nltk.word_tokenize(sent))
            candidates = candidate_lst[idx]
            for candidate in candidates:
                candidate_feature = self.extract_features(candidate,text,doc_word_counts)
                if candidate_feature != -1:
                    candidate_features[candidate] = candidate_feature
            candidate_features_lst.append(candidate_features)
        return candidate_features_lst

def stem_y(y_true):
    stemmer = PorterStemmer()
    for idx in xrange(len(y_true)):
        for idx_cand in xrange(len(y_true[idx])):
            y_true[idx][idx_cand] = ' '.join([stemmer.stem(word) for word in y_true[idx][idx_cand].split()])
    return y_true

if __name__ == '__main__':
    ids,X,y = load_data()
    to_stem = True
    # ids = ids[:50]
    # X = X[:50]
    # y = y[:50]
    pipeline = Pipeline([
        ('cleaner',DataClean(clean_list=[
                            # ["\."," . "],
                            ["[^a-z-]"," "],  # only letters,fullstops,hyphens(Note!)
                            [" [ ]+", " "],  # remove extra spaces
                            ])),
        ('candidate_features',CandidateFeatureExtractor()),
        ('keyword_selector',PairwiseRankingSVM(keyword_count=10,keyword_maxlen=5,stem=to_stem))
    ])
    # pipeline.fit(X,y)
    # pprint(pipeline.predict(X))
    # print pipeline.predict(X)[0]
    cross_validate((X,y),pipeline,keyword_prf,n_folds=4,stem_y=to_stem)