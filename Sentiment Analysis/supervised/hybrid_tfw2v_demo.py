from sklearn.pipeline import Pipeline,FeatureUnion
from sklearn.naive_bayes import BernoulliNB
from sklearn.feature_extraction.text import TfidfVectorizer
from pandas import read_csv
from nltk.corpus import stopwords
from bs4 import BeautifulSoup
from gensim.models import word2vec
from sklearn.cluster import KMeans
import numpy as np
import re
from sklearn.externals import joblib
import os

__author__ = 'tangy'

def load_data(tag="cornell"):
    if tag == "cornell":
        data_path = "../dataset/data_cornell_multilevel_sentiment.tsv"
        train_dframe = read_csv(data_path,sep = "\t")
        ids = train_dframe["PhraseId"].values
        X = train_dframe["Phrase"].values
        y = train_dframe["Sentiment"].values
        return ids,X,y
    elif tag == "stanford":
        data_path = "../dataset/data_stanford_binary_sentiment.tsv"
        train_dframe = read_csv(data_path,sep = "\t")
        ids = train_dframe["id"].values
        y = train_dframe["sentiment"].values
        X = train_dframe["review"].values
        return ids,X,y
    elif tag == "unsupervised":
        data_path = "../dataset/data_stanford_binary_sentiment_unlabelled.tsv"
        train_dframe = read_csv(data_path,sep = "\t",error_bad_lines=False)
        ids = train_dframe["id"].values
        X = train_dframe["review"].values
        return ids,X

class DataClean:
    """Cleans data by inputting list of regex to search and substitute
    Need to add stopword elimination support"""

    def __init__(self,clean_list,html_clean = False,split_words=False):
        self.clean_list = clean_list
        self.html_clean = html_clean
        self.split_words = split_words
        self.stopwords_eng = stopwords.words("english") + [u"film",u"movie"]


    def fit(self,X,y=None):
        return self

    def transform(self,X):
        X = X.flatten()
        X = map(self.clean_sentence,X)
        return np.array(X)

    def clean_sentence(self,sentence):
        if self.html_clean:
            sentence = BeautifulSoup(sentence).get_text()   #   removing html markup
        sentence = sentence.lower() #   everything to lowercase
        # sentence = ''.join(x for x in sentence if x.isalnum() or x==" ")
        for ch_rep in self.clean_list:
            sentence = re.sub(ch_rep[0],ch_rep[1],sentence)
        sentence = ' '.join(filter(lambda x:x not in self.stopwords_eng,sentence.split()))
        sentence = ' '.join(filter(lambda x:len(x) > 1,sentence.split()))
        sentence = sentence.strip(" ") # Remove possible extra spaces
        if self.split_words:
            sentence = sentence.split()
        return sentence

class Word2VecKMeans:
    """Converts words to vector representations derived from
    blackbox Word2Vec implementation"""

    def __init__(self,data_src,num_features=300):
        self.num_features = num_features
        self.pretrain(data_src)

    def pretrain(self,data_src):
        if not os.path.isfile("word2vecmodel.w2v"):
            data_src = DataClean([
                                ["[^a-z]"," "],  # only letters
                                [" [ ]+", " "],  # remove extra spaces
                                ],html_clean=True,split_words=True).fit(data_src).transform(data_src)
            self.model = word2vec.Word2Vec(data_src,workers=4,size=self.num_features,min_count=40,window=10,sample=1e-3) # min_count is minimum occur of the word
            self.model.init_sims(replace=True)  # If no more training is intended
            self.model.save("word2vecmodel.w2v")

    def fit(self,X,y=None):
        self.model = word2vec.Word2Vec.load("word2vecmodel.w2v")
        word_vectors = self.model.syn0
        num_clusters = word_vectors.shape[0]/5
        self.kmeans = KMeans(n_clusters=num_clusters,
                             n_jobs=-1)
        centroids = self.kmeans.fit_predict(word_vectors)
        self.word_centroid_dict = dict(zip(self.model.index2word,centroids))
        return self

    def inspect_clusters(self,n_clusters=None):
        centroids = self.word_centroid_dict.values()
        if n_clusters is None:
            n_clusters = len(list(set(centroids)))
        for cluster_idx in xrange(n_clusters):
            words = []
            for i in xrange(len(centroids)):
                if centroids[i] == cluster_idx:
                    words.append(self.word_centroid_dict.keys()[i])
            print "Cluster {}".format(cluster_idx)
            print words

    def sentence2vector(self,sentence):
        # Applying the Bag of Centroids technique
        sentence_tokens = sentence.split()
        feat_vect = np.zeros(max(self.word_centroid_dict.values()) + 1)
        word_vocab = self.word_centroid_dict.keys()
        for word in sentence_tokens:
            if word in word_vocab:
                feat_vect[self.word_centroid_dict[word]] += 1
        return feat_vect

    def transform(self,X):
        Xtf = np.vstack([self.sentence2vector(x) for x in X])
        return Xtf

    def fit_transform(self,X,y=None):
        self.fit(X,y)
        return self.transform(X)

def dump_model(clf):
    joblib.dump(clf,"smr_hybrid_clf.pkl",compress=9)

def load_model():
    return joblib.load("smr_hybrid_clf.pkl")

def train():
    _,unlabelledData = load_data("unsupervised")
    ids,X,y = load_data("cornell") # stanford/cornell
    # ids = ids[:10]
    # X = X[:10]
    # y = y[:10]
    pipeline = Pipeline([
        ('cleaner',DataClean(clean_list=[
                            ["[^a-z]"," "],  # only letters
                            [" [ ]+", " "],  # remove extra spaces
                            ],html_clean=False)),
        ('feature_extraction',FeatureUnion([
            ('w2v',Word2VecKMeans(data_src=unlabelledData)),
            ('tf',TfidfVectorizer())
            ])),
        ('classifier',BernoulliNB())
    ])
    print "fitting"
    pipeline.fit(X,y)
    print "dumping fitted model"
    dump_model(pipeline)

def test(sentence):
    clf = load_model()
    print sentence
    print clf.predict(np.array([sentence]))
