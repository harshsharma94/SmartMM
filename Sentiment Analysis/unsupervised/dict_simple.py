from utilities import load_data,cross_validate
from utilities import DataClean
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score
from pprint import pprint
from math import floor

class DictSimple:

    def __init__(self):
        dict_file = open("AFINN-96.txt")
        self.sentiment_dict = {}
        for line in dict_file:
            line = line.strip()
            field_val = line.split("\t")
            self.sentiment_dict[field_val[0]] = int(field_val[1])

    def fit(self,X,y):
        self.labels = list(set(y))
        self.labels.sort()
        return self

    def view_dictionary(self):
        pprint(self.sentiment_dict)

    def compute_score(self,sentence):
        sentence_score = 0
        for word in sentence.split():
            if word in self.sentiment_dict.keys():
                sentence_score += self.sentiment_dict[word]
        return sentence_score

    def predict(self,X):
        scores = [self.compute_score(x) for x in X]
        scores_max = max(scores)
        scores_min = min(scores)
        scores_normalized = []
        num_labels = len(self.labels)
        for score in scores:
            norm_score = float((score - scores_min))/(scores_max - scores_min)
            if norm_score == 1.0:
                norm_score -= 0.001
            elif norm_score == 0.0:
                norm_score += 0.001
            scores_normalized.append(norm_score)
        ypred = [self.labels[int(floor(score*num_labels))] for score in scores_normalized]
        return ypred



if __name__ == '__main__':
    ids,X,y = load_data("cornell")
    pipeline = Pipeline([
        ('cleaner',DataClean(clean_list=[
                            ["[^a-z]"," "],  # only letters
                            [" [ ]+", " "],  # remove extra spaces
                            ],html_clean=True)),
        ('classifier',DictSimple()),
    ])
    cross_validate((X,y),pipeline,accuracy_score)

# Cornell
# accuracy_score : 0.357580308161 +/- 0.156942834821
# Confusion Matrix
# [[  1.74000000e+02   4.14600000e+03   2.67400000e+03   7.30000000e+01
#     5.00000000e+00]
#  [  1.95000000e+02   1.44850000e+04   1.22810000e+04   2.97000000e+02
#     1.50000000e+01]
#  [  1.33000000e+02   3.89430000e+04   3.99920000e+04   5.05000000e+02
#     9.00000000e+00]
#  [  6.00000000e+01   1.20080000e+04   1.97190000e+04   1.08900000e+03
#     5.10000000e+01]
#  [  1.60000000e+01   2.50300000e+03   5.81500000e+03   8.08000000e+02
#     6.40000000e+01]]

# Stanford
# accuracy_score : 0.5608 +/- 0.0414194543663
# Confusion Matrix
# [[ 12155.    345.]
#  [ 10635.   1865.]]