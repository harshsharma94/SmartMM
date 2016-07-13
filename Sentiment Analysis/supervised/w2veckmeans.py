from utilities import load_data,cross_validate
from utilities import DataClean
from gensim.models import word2vec
from sklearn.cluster import KMeans
import os
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score
from sklearn.naive_bayes import BernoulliNB
from sklearn.ensemble import RandomForestClassifier

# Check notebook at :
# http://nbviewer.jupyter.org/github/MatthieuBizien/Bag-popcorn/blob/master/Kaggle-Word2Vec.ipynb

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
                                ],html_clean=True,split_words=True).fit(X).transform(X)
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


if __name__ == '__main__':
    _,unlabelledData = load_data("unsupervised")
    ids,X,y = load_data("cornell")
    pipeline = Pipeline([
        ('cleaner',DataClean(clean_list=[
                            ["[^a-z]"," "],  # only letters
                            [" [ ]+", " "],  # remove extra spaces
                            ],html_clean=False)),
        ('w2v',Word2VecKMeans(data_src=unlabelledData)),
        ('classifier',BernoulliNB())
    ])
    cross_validate((X,y),pipeline,accuracy_score)

# Stanford
# NB
# accuracy_score : 0.81932 +/- 0.00511171204197
# Confusion Matrix
# [[ 10361.   2139.]
#  [  2378.  10122.]]

# RF
# accuracy_score : 0.82656 +/- 0.00432592186707
# Confusion Matrix
# [[ 10411.   2089.]
#  [  2247.  10253.]]

# Cornell
# NB
# accuracy_score : 0.556138481746 +/- 0.00470505867585
# Confusion Matrix
# [[  1187.   2465.   2717.    529.    174.]
#  [  1544.   6131.  16370.   2716.    512.]
#  [   841.   4689.  68062.   5203.    787.]
#  [   564.   2274.  18582.   9723.   1784.]
#  [   165.    525.   2943.   3885.   1688.]]

# RF
# accuracy_score : 0.537395751584 +/- 0.0072332579528
# Confusion Matrix
# [[  7.27000000e+02   2.17700000e+03   3.47500000e+03   5.90000000e+02
#     1.03000000e+02]
#  [  9.05000000e+02   4.91800000e+03   1.84440000e+04   2.61200000e+03
#     3.94000000e+02]
#  [  5.21000000e+02   4.81000000e+03   6.71350000e+04   6.39200000e+03
#     7.24000000e+02]
#  [  1.93000000e+02   1.69700000e+03   1.94890000e+04   9.49100000e+03
#     2.05700000e+03]
#  [  5.10000000e+01   3.93000000e+02   3.26500000e+03   3.90200000e+03
#     1.59500000e+03]]