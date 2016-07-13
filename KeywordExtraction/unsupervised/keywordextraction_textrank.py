from utilities import CandidateSelection,DataClean
from utilities import load_data,cross_validate
from sklearn.pipeline import Pipeline
from keyword_metrics import keyword_prf,keyword_prf_onegram
from nltk.stem import PorterStemmer
from itertools import takewhile, tee, izip
import networkx, nltk

class TextRank_KeywordSelection:

    def __init__(self,keyword_count,stem=True):
        self.keyword_count = keyword_count
        self.stem = stem
        if self.stem:
            self.stemmer = PorterStemmer()

    def fit(self,X,y=None):
        return self

    def predict(self,X):
        if self.stem:
            Xstem = []
            for idx in range(len(X)):
                xstem = []
                for sent in nltk.sent_tokenize(X[idx]):
                    sentstem = []
                    for word in nltk.word_tokenize(sent):
                        if word != ".":
                            sentstem.append(self.stemmer.stem(word))
                    xstem.append(' '.join(sentstem))
                Xstem.append('.'.join(xstem))
            X = Xstem
        ypred = self.score_keyphrases_by_textank(X,False)
        return ypred


    def score_keyphrases_by_textank(self, X,phrase=True):
        candidates_lst = CandidateSelection(method="nounadj_tags_heuristic_words").fit_transform(X)
        keywords_lst = []
        for idx in xrange(len(X)):
            text = X[idx]
            words = [word for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
            graph = networkx.Graph()
            candidates = candidates_lst[idx]
            graph.add_nodes_from(set(candidates))
            def pairwise(iterable):
                """s -> (s0,s1), (s1,s2), (s2, s3), ...
                iterable -> (keyword1,keyword2),keyword2,keyword3),..."""
                a, b = tee(iterable)
                next(b, None)
                return izip(a, b)
            for keyword1,keyword2 in pairwise(candidates):
                if keyword2:
                    # Directed Graph, thus sort and insert
                    graph.add_edge(*sorted([keyword1,keyword2]))
            # score nodes using default pagerank algorithm, sort by score, keep top n_keywords
            ranks = networkx.pagerank(graph)
            word_ranks = {word_rank[0]: word_rank[1]
                         for word_rank in sorted(ranks.iteritems(),key=lambda x: x[1],reverse=True)[:self.keyword_count]}
            keywords = set(word_ranks.keys())
            if phrase:
                # merge keywords into keyphrases
                keyphrases = {}
                j = 0
                for i,word in enumerate(words):
                    if i < j:
                        continue
                    if word in keywords:
                        kp_words = list(takewhile(lambda x:x in keywords, words[i:i+10]))
                        if len(kp_words) != len(set(kp_words)):
                            continue # No repitions
                        avg_pagerank = sum(word_ranks[w] for w in kp_words)/float(len(kp_words))
                        keyphrases[' '.join(kp_words)] = avg_pagerank
                        # to ensure merged keywords are not overlapping
                        j = i + len(kp_words)
                keywords_lst.append([x[0] for x in sorted(keyphrases.iteritems(),key=lambda x: x[1],reverse = True)[:self.keyword_count]])
            else:
                keywords_lst.append(keywords)
        return keywords_lst



if __name__ == '__main__':
    ids,docs,keywords_doc = load_data()
    ids = ids
    docs = docs
    keywords_doc = keywords_doc
    pipeline = Pipeline([
        ('cleaner',DataClean(clean_list=[
                            ["[^a-z\.-]"," "],  # only letters,fullstops
                            [" [ ]+", " "],  # remove extra spaces
                            ])),
        ('keyword_selector',TextRank_KeywordSelection(keyword_count=10,stem=True))
    ])
    cross_validate((docs,keywords_doc),pipeline,keyword_prf,stem_y=True)

# keyword_prf_onegram - top 10 keywords - NounAdj Heuristic Word Extracter
# precision_score : 0.460607928569 +/- 0.0223582417735
# recall_score : 0.101528291878 +/- 0.00369494108571
# f1_score : 0.1663268895 +/- 0.00566981557492

# keyword_prf - top 10 keywords - NounAdj Heuristic Word Extracter
# precision_score : 0.102777777778 +/- 0.0114530711823
# recall_score : 0.0662220027866 +/- 0.00674066818071
# f1_score : 0.0805386324756 +/- 0.00848527696726

# keyword_prf_onegram - top 15 keywords - NounAdj Heuristic Word Extracter

# keyword_prf - top 15 keywords - NounAdj Heuristic Word Extracter

