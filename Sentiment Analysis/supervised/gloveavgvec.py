from utilities import load_data,cross_validate
from utilities import DataClean
import os
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score
from sklearn.naive_bayes import BernoulliNB
from sklearn.ensemble import RandomForestClassifier
from glove import Corpus,Glove

class Glove2AverageVector:
    """Converts words to vector representations derived from
    blackbox Word2Vec implementation"""

    def __init__(self,data_src,num_features=100,window=10,learning_rate=0.05,epochs=10):
        self.learning_rate = learning_rate
        self.num_features = num_features
        self.window = window
        self.epochs = epochs
        self.pretrain(data_src)
        self.model = Glove.load("glove.model")

    def pretrain(self,data_src):
        if not os.path.isfile("glove.model"):
            data_src = DataClean([
                                ["[^a-z]"," "],  # only letters
                                [" [ ]+", " "],  # remove extra spaces
                                ],html_clean=True,split_words=True).fit(data_src).transform(data_src)
            corpus_model = Corpus()
            corpus_model.fit(data_src,window=self.window)
            glove = Glove(no_components=self.num_features,learning_rate=self.learning_rate)
            glove.fit(corpus_model.matrix,epochs=self.epochs,verbose=True)
            glove.add_dictionary(corpus_model.dictionary)
            glove.save("glove.model")

    def fit(self,X,y=None):
        self.model = Glove.load("glove.model")
        return self

    def sentence2vector(self,sentence):
        sentence_tokens = sentence.split()
        nwords = 0.01
        feat_vect = np.zeros(self.num_features)
        # index2word_set = set(self.model.dictionary.keys())
        for word in sentence_tokens:
            try:
                feat_vect += self.model.word_vectors[self.model.dictionary[word]]
                nwords += 1
            except:
                continue
        return feat_vect/nwords

    def transform(self,X):
        Xtf = np.vstack([self.sentence2vector(x) for x in X])
        return Xtf

    def fit_transform(self,X,y=None):
        self.fit(X,y)
        return self.transform(X)


if __name__ == '__main__':
    _,unlabelledData = load_data("unsupervised")
    ids,X,y = load_data("stanford")
    pipeline = Pipeline([
        ('cleaner',DataClean(clean_list=[
                            ["[^a-z]"," "],  # only letters
                            [" [ ]+", " "],  # remove extra spaces
                            ],html_clean=False)),
        ('w2v',Glove2AverageVector(data_src=unlabelledData)),
        ('classifier',RandomForestClassifier(n_estimators=100))
    ])
    cross_validate((X,y),pipeline,accuracy_score)

# num_features=100,window=10,learning_rate=0.05,epochs=10
# Stanford
# NB
# accuracy_score : 0.72772 +/- 0.00562665086886
# Confusion Matrix
# [[ 9223.  3277.]
#  [ 3530.  8970.]]
# RF
# accuracy_score : 0.78932 +/- 0.00245373185169
# Confusion Matrix
# [[  9644.   2856.]
#  [  2411.  10089.]]

# Cornell
# NB
# accuracy_score : 0.24543076998 +/- 0.0117745086102
# Confusion Matrix
# [[  3869.    138.    403.    338.   2324.]
#  [ 10873.    731.   3809.   2459.   9401.]
#  [ 20249.   2433.  23007.  11613.  22280.]
#  [  7298.    399.   3611.   3818.  17801.]
#  [  1391.     27.    285.    626.   6877.]]
# RF
# accuracy_score : 0.538638825433 +/- 0.00677413249639
# Confusion Matrix
# [[  3.16000000e+02   2.02600000e+03   4.05700000e+03   6.43000000e+02
#     3.00000000e+01]
#  [  3.72000000e+02   4.67800000e+03   1.92160000e+04   2.92600000e+03
#     8.10000000e+01]
#  [  1.92000000e+02   4.43700000e+03   6.81370000e+04   6.59400000e+03
#     2.22000000e+02]
#  [  3.90000000e+01   1.56000000e+03   2.03260000e+04   1.01990000e+04
#     8.03000000e+02]
#  [  3.00000000e+00   3.39000000e+02   3.79100000e+03   4.34300000e+03
#     7.30000000e+02]]


