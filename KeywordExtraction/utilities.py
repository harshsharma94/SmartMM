from sklearn.cross_validation import KFold
import csv
import numpy as np
from bs4 import BeautifulSoup
import re
from nltk.corpus import stopwords
import os
from nltk.stem import PorterStemmer

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

class CandidateSelection:

    def __init__(self,method="noun_phrase_heuristic_chunks"):
        assert method in ["noun_phrase_heuristic_chunks","nounadj_tags_heuristic_words"],\
            "`method` must be one of `noun_phrase_heuristic_chunks`/`nounadj_tags_heuristic_words`"
        self.method = method

    def fit(self,X,y=None):
        return self

    def transform(self,X):
        if self.method == "noun_phrase_heuristic_chunks":
            keywords = [self.extract_candidate_chunks_noun_phrase_heuristic(text) for text in X]
        else:
            keywords = [self.extract_candidate_words_nounadj_tags_heuristic(text) for text in X]
        return keywords

    def fit_transform(self,X,y=None):
        self.fit(X,y)
        return self.transform(X)

    def extract_candidate_chunks_noun_phrase_heuristic(self, text, grammar=r'KT: {(<JJ>* <NN.*>+ <IN>)? <JJ>* <NN.*>+}'):
        import itertools, nltk, string
        """Return all those words as candidates which follow a specific pos_tag pattern"""

        # exclude candidates that are stop words or entirely punctuation
        punct = set(string.punctuation)
        stop_words = set(nltk.corpus.stopwords.words('english'))
        # tokenize, POS-tag, and chunk using regular expressions
        chunker = nltk.chunk.regexp.RegexpParser(grammar)
        tagged_sents = nltk.pos_tag_sents(nltk.word_tokenize(sent) for sent in nltk.sent_tokenize(text))
        all_chunks = list(itertools.chain.from_iterable(nltk.chunk.tree2conlltags(chunker.parse(tagged_sent))
                                                        for tagged_sent in tagged_sents))
        # join constituent chunk words into a single chunked phrase
        candidates = [' '.join(word for word, pos, chunk in group).lower()
                      for key, group in itertools.groupby(all_chunks, lambda (word,pos,chunk): chunk != 'O') if key]

        return [cand for cand in candidates
                if cand not in stop_words and not all(char in punct for char in cand)]

    def extract_candidate_words_nounadj_tags_heuristic(self, text, good_tags=set(['JJ','JJR','JJS','NN','NNP','NNS','NNPS'])):
        """Return all those words as candidates which are good_tags - here theyre nouns/adjectives """
        import itertools, nltk, string

        # exclude candidates that are stop words or entirely punctuation
        punct = set(string.punctuation)
        stop_words = set(nltk.corpus.stopwords.words('english'))
        # tokenize and POS-tag words
        tagged_words = itertools.chain.from_iterable(
            nltk.pos_tag_sents(nltk.word_tokenize(sent) for sent in nltk.sent_tokenize(text)))
        # filter on certain POS tags and lowercase all words
        candidates = [word.lower() for word, tag in tagged_words
                      if tag in good_tags and word.lower() not in stop_words
                      and not all(char in punct for char in word)]
        return candidates

def load_data(tag="semeval"):
    if tag == "semeval":
        data_path = "../dataset/semeval2010"
        X = []
        y = []
        ids = []
        for f in os.listdir(data_path):
            f = os.path.join(data_path,f)
            if f.endswith("txt"):
                fname = f.replace(".txt","")
                ids.append(fname)
                key_file = "{}.key".format(fname)
                with open(f) as articlefile:
                    article = articlefile.read()
                    X.append(article)
                with open(key_file) as keywords_file:
                    keywords = keywords_file.readlines()
                    keywords_cleaned = [keyword.strip() for keyword in keywords]
                    y.append(keywords_cleaned)
    elif tag == "imdbpy_plotkeywords":
        data_path = "../dataset/imdbpy_plotkeywords.csv"
        X = []
        y = []
        ids = []
        with open(data_path) as f:
            csv_f = csv.reader(f)
            for row in csv_f:
                num_plot_summaries = int(row[2])
                plots = []
                for i in xrange(num_plot_summaries):
                    plots.append(row[i+3])
                plots = " ".join(plots)
                keywords_idx = num_plot_summaries + 3
                keywords = []
                for i in xrange(keywords_idx,len(row)):
                    keyword = row[i]
                    keyword_alt = keyword.replace("-"," ")
                    if keyword_alt in plots or keyword in plots:
                        keywords.append(keyword_alt)
                if len(keywords) > 4:
                    ids.append(row[0])
                    X.append(plots)
                    y.append(keywords)
    else:
        raise("`tag` must be one of `semeval`,`imdbpy_plotkeywords`")
    return ids,np.array(X),np.array(y)

def cross_validate(data,pipeline,metric_apply,n_folds = 4,stem_y=True):
    (X,y) = data
    if stem_y:
        stemmer = PorterStemmer()
        y_stem = []
        for keywords in y:
            keywords_stemmed = []
            for keyword in keywords:
                try:
                    stemmed_keyword = stemmer.stem(keyword.decode('utf-8'))
                    keywords_stemmed.append(stemmed_keyword)
                except Exception as e:
                    print "Error stemming keyword %s, Skipping." % keyword
            y_stem.append(keywords_stemmed)
            y = np.array(y_stem)
    skf = KFold(len(y),n_folds=n_folds)
    precision_score = []
    recall_score = []
    f1_score = []
    metric_apply = metric_apply
    counter = 0
    for train_idx,val_idx in skf:
        counter += 1
        print "Running fold %d" % counter
        print "fitting"
        pipeline.fit(X[train_idx],y[train_idx])
        print "predicting"
        ypred = pipeline.predict(X[val_idx])
        p,r,f = metric_apply(y[val_idx],ypred)
        precision_score.append(p)
        recall_score.append(r)
        f1_score.append(f)
    print metric_apply.__name__
    print "{} : {} +/- {}".format("precision_score",
                                  np.mean(precision_score),
                                  np.std(precision_score))
    print "{} : {} +/- {}".format("recall_score",
                                  np.mean(recall_score),
                                  np.std(recall_score))
    print "{} : {} +/- {}".format("f1_score",
                                  np.mean(f1_score),
                                  np.std(f1_score))
