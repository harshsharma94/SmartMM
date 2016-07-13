from __future__ import division
import gensim
import logging
import pysrt
from string import punctuation
import numpy
from scipy import spatial
import os
from nltk.corpus import sentiwordnet as swn
from nltk.corpus import wordnet as wn
import csv
from nltk.corpus import stopwords
from sklearn import svm
import pickle

#SRTdata = "SRT/SRT_db/extract/"

#SRTdataFileName = glob.glob(SRTdata + "50.First.Dates.DVDRip.XViD-ALLiANCE.srt")

#print testFileNames
#print subtitleFileNames
# print predictFileNames
count_total = 0
emotion_list = []
movie_names=[]

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
model = ""
majorEmo = ["happy", "surprise", "sad", "disgust", "anger", "fear"]

testEmo = []
for emo in majorEmo:
    testEmo.append(emo)
testEmo.append("emotionless")

majorEmotionsForStringForComparison = ["happy", "surprise", "emotionless", "sad", "disgust", "anger", "fear"]
testEmo_forSVM = ["happy", "surprise", "emotionless", "sad", "disgust", "anger", "fear"]

ifRemoveStopWords = True
ifUseSentiWordNet = True
sentiWordNet_ThreshHold = 0.2
sentiWordNet_majorEmo_ThreshHold = 0.1
ifReweight_using_sentiWordNet = True


class Emotion:
    emoCount = 0

    def __init__(self, name):
        self.name = name
        Emotion.emoCount += 1
        self.true_pos = 0
        self.true_neg = 0
        self.false_pos = 0
        self.false_neg = 0
        self.accuracy = -1.0
        self.precision = -1.0

    def printObj(self):
        if self.true_pos + self.true_neg > 0:
            self.accuracy = self.true_pos / (self.true_pos + self.true_neg)

        if self.true_pos + self.false_pos > 0:
            self.precision = self.true_pos / (self.true_pos + self.false_pos)

        print "Emotion: ", self.name
        print "True Positive: ", self.true_pos, "\t", "True negative: ", self.true_neg
        print "False Positive: ", self.false_pos, "\t", "False negative: ", self.false_neg
        print "Accuracy: ", 100.0 * self.accuracy, "%\t", "Precision: ", 100.0 * self.precision, "%"

    def clear_stats(self):
        self.true_pos = 0
        self.true_neg = 0
        self.false_pos = 0
        self.false_neg = 0
        self.accuracy = -1.0
        self.precision = -1.0


emoObjs = {}
for emo in testEmo:
    emoObj = Emotion(emo)
    emoObjs[emo] = emoObj


def parse(subtitleFileName):
    subtitleText = []
    try:
        subtitleLines = pysrt.open(subtitleFileName, encoding='utf-8')
        for i in range(len(subtitleLines)):
            # print subtitleLines[i].text
            lineNoPunct = ' '.join(filter(None, (word.strip(punctuation) for word in subtitleLines[i].text.split())))
            allWords = lineNoPunct.split()
            allWords = [x.lower() for x in allWords]
            subtitleText.append(allWords)
        return subtitleText
    except:
        return 0


def load_model():
    #print"hi! starting to load model"
    global model
    model = gensim.models.Word2Vec.load("emotion_word2vec")
    #print"hi! loading model done"
    # self.model = word2vec.Word2Vec.load("word2vecmodel.w2v")




def remove_stopwords_from_line(line):
    stops = set(stopwords.words("english"))
    lineNoPunct = ' '.join(filter(None, (word.strip(punctuation) for word in line)))#line.split()
    allWords = lineNoPunct.split()
    allWords = [x.lower() for x in allWords]
    # print "before removing stopwords: ", allWords
    allWords = [w for w in allWords if not w in stops]
    # print "after removing stopwords: ", allWords
    return allWords


def remove_nonSentiWord(word):
    shouldInclude = False
    if len(list(swn.senti_synsets(word))) == 0:
        # print word, " not in sentiWordNet"
        if len(list(wn.synsets(word))) == 0:
            # print word, " not in wordNet"
            shouldInclude = False
        else:
            shouldInclude = True
    else:
        synSet = list(swn.senti_synsets(word))
        # print "Word: ", word
        for item in synSet:
            # print "+ ", item.pos_score(), " - ", item.neg_score(), " Neutral ", item.obj_score()
            if item.pos_score() > sentiWordNet_ThreshHold or item.neg_score() > sentiWordNet_ThreshHold:
                shouldInclude = True
                break
    return shouldInclude


def get_net_pos_neg(word):
    netPos = 0
    netNeg = 0

    if len(list(swn.senti_synsets(word))) != 0:
        sentisyn = list(swn.senti_synsets(word))
        for item in sentisyn:
            netPos += item.pos_score()
            netNeg += item.neg_score()

    return netPos, netNeg



def predictEmo(predictfilename ,emoVecs):
    majorEmoReallyUsed=['happy', 'surprise', 'sad', 'anger', 'fear']
    percent =[]
    subtitleText = []
    labeledEmotions = []
    senVec = 0
    emotionlessCount = 0
    emoCount = [0] * len(majorEmoReallyUsed)
    if (parse(predictfilename) != 0):
        print predictfilename
        movie_names.append(predictfilename)
        subtitleLines = parse(predictfilename)
        allsenVec = []
        for i in range(len(subtitleLines)):
            allWords = remove_stopwords_from_line(subtitleLines[i])
            subtitleText.append(allWords)
            usedWords = []
            numWords = 0
            for word in allWords:
                if ifUseSentiWordNet == True:
                    if remove_nonSentiWord(word) == False:
                        continue
                if word in model.vocab.keys():
                    wordVec = model[word]
                    wordVec = numpy.array(wordVec)
                    if numWords >= 1:
                        senVec += wordVec
                    else:
                        senVec = wordVec
                    numWords += 1
                    usedWords.append(word)
            if numWords == 0:
                emotionlessCount += 1
                labeledEmotions.append(len(majorEmoReallyUsed))
                continue
            senVec = senVec / numWords
            allsenVec.append(senVec)
            # y.append(trueEmotions[i])
            minDis = 1
            count = 0
            for emoVec in emoVecs:
                try:
                    emoDis = spatial.distance.cosine(emoVec,senVec)
                except:
                    emoDis = 1
                if emoDis < minDis:
                    bestEmo = count
                    minDis = emoDis
                count += 1
            if minDis < 1:
                emoCount[bestEmo] += 1
                labeledEmotions.append(bestEmo)
            else:
                emotionlessCount += 1
                labeledEmotions.append(len(majorEmoReallyUsed))
        global count_total
        count_total +=1
        max=0
        for i in range(len(emoCount)):
            if emoCount[i] > max:
                max = emoCount[i]
                maxIndex = i
        print "major emotion of the movie: " + majorEmoReallyUsed[maxIndex]
        emotion_list.append(majorEmoReallyUsed[maxIndex])
        # % of each emotion excluding emotionless
        print "percentage per emotion: "
        for i in range(len(majorEmoReallyUsed)):
            percent.append(emoCount[i] / len(allsenVec))

        dict = {}
        for i in range(len(majorEmoReallyUsed)):
            dict[majorEmoReallyUsed[i]] = percent[i]

        return dict



def initialize_emotion_recognizer():
    load_model()
    emovecs= pickle.load( open( "emotion_recognizer_wts.pickle", "rb" ) )
    return emovecs
    #predict('batman-the-dark-knight-returns-part-2-yify-english.srt',emovecs)


# total srt :54
#correct prediction: 30
#percentage : 0.555555555556
