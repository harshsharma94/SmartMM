from utilities import load_data,cross_validate
from utilities import DataClean
from gensim.models import word2vec
import os
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score
from sklearn.naive_bayes import BernoulliNB
from sklearn.ensemble import RandomForestClassifier

# Check notebook at :
# http://nbviewer.jupyter.org/github/MatthieuBizien/Bag-popcorn/blob/master/Kaggle-Word2Vec.ipynb

class Word2VecAverageVector:
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
        return self

    def sentence2vector(self,sentence):
        sentence_tokens = sentence.split()
        nwords = 0.01
        feat_vect = np.zeros(self.num_features)
        index2word_set = set(self.model.index2word)
        for word in sentence_tokens:
            if word in index2word_set:
                feat_vect += self.model[word]
                nwords += 1
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
                            ],html_clean=True)),
        ('w2v',Word2VecAverageVector(data_src=unlabelledData)),
        ('classifier',BernoulliNB())
    ])
    cross_validate((X,y),pipeline,accuracy_score)

# Stanford
# NB
# accuracy_score : 0.74804 +/- 0.00429827872526
# Confusion Matrix
# [[ 9781.  2719.]
#  [ 3580.  8920.]]
# RF
# accuracy_score : 0.83888 +/- 0.0026241951147
# Confusion Matrix
# [[ 10281.   2219.]
#  [  1809.  10691.]]

# Cornell
# NB
# accuracy_score : 0.365474467821 +/- 0.00923504308774
# Confusion Matrix
# [[  4158.    843.    701.    703.    667.]
#  [  9371.   4245.   5826.   4753.   3078.]
#  [ 10631.   9510.  33523.  17277.   8641.]
#  [  4158.   2736.   5604.   9488.  10941.]
#  [   877.    376.    478.   1853.   5622.]]
# RF
# accuracy_score : 0.549506499923 +/- 0.00297006896089
# Confusion Matrix
# [[  2.95000000e+02   2.46500000e+03   3.85100000e+03   4.54000000e+02
#     7.00000000e+00]
#  [  3.74000000e+02   4.51600000e+03   2.01680000e+04   2.18500000e+03
#     3.00000000e+01]
#  [  1.86000000e+02   3.52400000e+03   7.03170000e+04   5.37600000e+03
#     1.79000000e+02]
#  [  4.60000000e+01   9.96000000e+02   2.11890000e+04   1.00520000e+04
#     6.44000000e+02]
#  [  8.00000000e+00   1.91000000e+02   3.56800000e+03   4.86300000e+03
#     5.76000000e+02]]
