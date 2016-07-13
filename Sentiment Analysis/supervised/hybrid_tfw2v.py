from utilities import load_data,cross_validate
from utilities import DataClean
import numpy as np
from sklearn.pipeline import Pipeline,FeatureUnion
from sklearn.metrics import accuracy_score
from sklearn.naive_bayes import BernoulliNB
from sklearn.ensemble import RandomForestClassifier
from w2veckmeans import Word2VecKMeans
from tf_bow import TfidfVectorizer

__author__ = 'tangy'

if __name__ == '__main__':
    _,unlabelledData = load_data("unsupervised")
    ids,X,y = load_data("cornell") # stanford/cornell
    pipeline = Pipeline([
        ('cleaner',DataClean(clean_list=[
                            ["[^a-z]"," "],  # only letters
                            [" [ ]+", " "],  # remove extra spaces
                            ],html_clean=False)),
        ('feature_extraction',FeatureUnion([
            ('w2v',Word2VecKMeans(data_src=unlabelledData)),
            ('tf',TfidfVectorizer())
            ])),
        ('classifier',BernoulliNB()) # BernoulliNB(),RandomForestClassifier(n_estimators=100,n_jobs=-1)
    ])
    cross_validate((X,y),pipeline,accuracy_score)

# Stanford
# NB

# RF

# Cornell
# NB
# accuracy_score : 0.566281897396 +/- 0.00906813346642
# Confusion Matrix
# [[  1368.   3027.   2085.    400.    192.]
#  [  1960.   8002.  14148.   2524.    639.]
#  [  1029.   6207.  64562.   6562.   1222.]
#  [   644.   2288.  15151.  12131.   2713.]
#  [   162.    377.   1955.   4401.   2311.]]

# RF
