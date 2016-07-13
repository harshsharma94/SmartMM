from utilities import load_data,cross_validate
from utilities import DataClean
from sklearn.naive_bayes import BernoulliNB
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score



if __name__ == '__main__':
    ids,X,y = load_data("stanford")
    pipeline = Pipeline([
        ('cleaner',DataClean(clean_list=[
                            ["[^a-z]"," "],  # only letters
                            [" [ ]+", " "],  # remove extra spaces
                            ],html_clean=True)),
        ('tf',TfidfVectorizer(use_idf=True,stop_words="english")),
        ('classifier',BernoulliNB())
    ])
    cross_validate((X,y),pipeline,accuracy_score)

# Cornell
# accuracy_score : 0.561444222777 +/- 0.00476207774317
# Confusion Matrix
# [[   744.   2936.   2872.    420.    100.]
#  [   967.   6398.  17320.   2216.    372.]
#  [   435.   4617.  68438.   5425.    667.]
#  [   271.   1767.  18586.  10745.   1558.]
#  [    71.    337.   2807.   4697.   1294.]]

# Stanford
# accuracy_score : 0.84216 +/- 0.00601916937791
# Confusion Matrix
# [[ 11085.   1415.]
#  [  2531.   9969.]]