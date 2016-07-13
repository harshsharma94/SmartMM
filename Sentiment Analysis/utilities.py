from sklearn.cross_validation import StratifiedKFold
from pandas import read_csv
import numpy as np
from sklearn.metrics import confusion_matrix
from bs4 import BeautifulSoup
import re
from nltk.corpus import stopwords


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

    def __repr__(self):
        return "DataClean"

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


def cross_validate(data,pipeline,metric_apply,n_folds = 4):
    (X,y) = data
    skf = StratifiedKFold(y,n_folds=n_folds)
    metric = []
    num_labels = len(list(set(y)))
    conf_matrix = np.zeros((num_labels,num_labels))
    counter = 0
    for train_idx,val_idx in skf:
        counter += 1
        print "Running fold %d" % counter
        print "fitting"
        pipeline.fit(X[train_idx],y[train_idx])
        print "predicting"
        ypred = pipeline.predict(X[val_idx])
        metric.append(metric_apply(y[val_idx],ypred))
        conf_matrix += confusion_matrix(y[val_idx],ypred)
    print "{} : {} +/- {}".format(metric_apply.func_name,
                                  np.mean(metric),
                                  np.std(metric))
    print "Confusion Matrix"
    print conf_matrix