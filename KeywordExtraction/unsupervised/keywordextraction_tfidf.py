from utilities import CandidateSelection,DataClean
from utilities import load_data,cross_validate
from sklearn.pipeline import Pipeline
from keyword_metrics import keyword_prf,keyword_prf_onegram
from nltk.stem import PorterStemmer
import networkx, nltk
import gensim

class Tfidf_KeywordSelection:

    def __init__(self,keyword_count,stem=True):
        self.keyword_count = keyword_count
        self.stem = stem
        if self.stem:
            self.stemmer = PorterStemmer()

    def fit(self,X,y=None):
        return self

    def predict(self,X):
        if self.stem:
            for idx in xrange(len(X)):
                for idx_cand in xrange(len(X[idx])):
                    X[idx][idx_cand] = " ".join([self.stemmer.stem(word) for word in X[idx][idx_cand].split()])
        corpus_tfidf,dictionary = self.score_keyphrases_by_tfidf(X)
        ypred = []
        for scores in corpus_tfidf:
            scores = sorted(scores,key=lambda x:x[1],reverse=True)[:self.keyword_count]
            ypred.append([dictionary[word_idx] for word_idx,score in scores])
        return ypred


    def score_keyphrases_by_tfidf(self, candidates):
        # make gensim dictionary and corpus
        dictionary = gensim.corpora.Dictionary(candidates)
        corpus = [dictionary.doc2bow(candidate) for candidate in candidates]
        # transform corpus with tf*idf model
        tfidf = gensim.models.TfidfModel(corpus)
        corpus_tfidf = tfidf[corpus]
        return corpus_tfidf, dictionary

if __name__ == '__main__':
    ids,docs,keywords_doc = load_data()
    ids = ids[:50]
    docs = docs[:50]
    keywords_doc = keywords_doc[:50]
    to_stem=True
    pipeline = Pipeline([
        ('cleaner',DataClean(clean_list=[
                            ["[^a-z\.-]"," "],  # only letters,fullstops
                            [" [ ]+", " "],  # remove extra spaces
                            ])),
        ('candidate_selector',CandidateSelection()),
        ('keyword_selector',Tfidf_KeywordSelection(keyword_count=10,stem=to_stem))
    ])
    pipeline.fit(docs,keywords_doc)
    cross_validate((docs,keywords_doc),pipeline,keyword_prf_onegram,stem_y=to_stem)
    # print pipeline.predict(docs)
    # print keywords_doc

# keyword_prf_onegram - top 10 keywords - NounAdj Heuristic Word Extracter

# keyword_prf - top 10 keywords - NounAdj Heuristic Word Extracter

# keyword_prf_onegram - top 15 keywords - NounAdj Heuristic Word Extracter

# keyword_prf - top 15 keywords - NounAdj Heuristic Word Extracter

