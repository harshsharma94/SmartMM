#TODO Subtitle Emotions,

import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
import functools
from PyQt5.QtWebKitWidgets import *
from gui import Ui_MainWindow
from PyQt5.QtCore import QCoreApplication
from rake import *
from textrank import *
import nltk
from contentBasedRecommender import *
import qdarkstyle
from wordcloud import WordCloud
from utilities import *
import StringIO
import base64
import qtawesome as qta
from random import randint
sys.modules['PyQt4.QtGui'] = QtGui
from PIL.ImageQt import ImageQt
from hybrid_tfw2v_demo import *
from emotion_recognizer import predictEmo,initialize_emotion_recognizer

class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle('SmartMM')
        self.initialize()

    def initialize(self):
        first_load()
        self.emovecs = initialize_emotion_recognizer()
        self.initalize_gui()
        self.initialize_triggers()

    def initalize_gui(self):
        self.ui.review1.setStyleSheet("background-color: DarkCyan;color: black")
        self.ui.recommendButton.setStyleSheet("background-color: Tomato;color: black")
        self.ui.review1.setIcon(qta.icon('fa.flag'))
        self.ui.recommendButton.setIcon(qta.icon('fa.bullseye'))
        self.setup_mov_list()
        self.ui.progressInfo.setVisible(False)
        self.ui.progressBar.setVisible(False)
        self.showClickedItem(self.ui.listWidget.item(0))

    def initialize_triggers(self):
        self.ui.actionExit.triggered.connect(QCoreApplication.instance().quit)
        self.ui.actionAdd_Files.triggered.connect(self.addFiles_triggered)
        self.ui.actionAdd_Folders.triggered.connect(self.addFolder_triggered)
        self.ui.listWidget.itemClicked.connect(self.showClickedItem)
        self.ui.actionSync.triggered.connect(self.internet_sync_trigger)
        self.ui.recommendButton.clicked.connect(self.recommendMovies)

    #The list shows movies even if movie is removed from folder
    def recommendMovies(self):
        list = getSeenMovies()
        list = [x[0] for x in list]
        print list
        recommender = Recommender()
        rec_list = recommender.get_n_recommendations(10, list)
        for movie in rec_list:
            self.ui.listWidgetRecommend.addItem(movie['title'])

    def setup_mov_list(self):
        movies = get_mov_names()
        self.ui.listWidget.clear()
        #check if the movie exists in the folder acc. to db entry
        #correct it
        for movie in movies:
            if movie != "":
                print movie
                item = QtWidgets.QListWidgetItem()
                widget = QtWidgets.QWidget()
                widgetText = QtWidgets.QLabel(movie)
                widgetCheckbox = QtWidgets.QCheckBox()
                path = os.getcwd()
                widgetCheckbox.setStyleSheet(
                    "QCheckBox::indicator:unchecked {image: url(%s/images/star_greyed_small.png);}"
                    "QCheckBox::indicator:checked {image: url(%s/images/star_pressed_small.png);}" % (path,path)
                )
                widgetLayout = QtWidgets.QHBoxLayout()
                widgetLayout.addWidget(widgetText)
                widgetLayout.addStretch(1)
                widgetLayout.addWidget(widgetCheckbox)
                widget.setLayout(widgetLayout)
                item.setSizeHint(widget.sizeHint())
                seen = getSeenValue(movie)
                #print movie + " Initial Seen Value: " + str(seen)
                if seen:
                    widgetCheckbox.setCheckState(QtCore.Qt.Checked)
                #print checkbox.isChecked()
                widgetCheckbox.stateChanged.connect(functools.partial(self.checkFunction, movie))
                self.ui.listWidget.addItem(item)
                self.ui.listWidget.setItemWidget(item, widget)

                ####OLD CODE WITHOUT LABEL
                """
                #print movie
                item = QtWidgets.QListWidgetItem(movie)
                self.ui.listWidget.addItem(item)
                checkbox = QtWidgets.QCheckBox()
                seen = getSeenValue(movie)
                #print movie + " Initial Seen Value: " + str(seen)
                if seen:
                    checkbox.setCheckState(QtCore.Qt.Checked)
                #print checkbox.isChecked()
                checkbox.stateChanged.connect(functools.partial(self.checkFunction, movie))
                self.ui.listWidget.setItemWidget(item, checkbox)
                """

    def checkFunction(self, movie):
        #if state == QtCore.Qt.Checked:
        changeSeenValue(movie)

    def addFolder_triggered(self):
        dir = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory"))
        add_folder(dir)
        self.setup_mov_list()

    def addFiles_triggered(self):
        filename=QtWidgets.QFileDialog.getOpenFileName(self)
        add_file(filename[0])
        self.setup_mov_list()

    def displayImage(self, imgData):
        qimg = QtGui.QImage.fromData(imgData)
        pixmap = QtGui.QPixmap.fromImage(qimg)
        self.ui.imgLabel.setPixmap(pixmap)

    def showClickedItem(self,item):
        #selected_vid = item.text()
        try:
            selected_vid = self.ui.listWidget.itemWidget(item).findChild(QtWidgets.QLabel).text()
            self.update_gui_with_mov(selected_vid)
        except Exception as e:
            print e.message



    def update_gui_with_mov(self,mov):
        mov_details = prep_mov_details_dict(mov_to_id(mov))
        print mov_details
        #print len(mov_details["review_urls"])
        self.ui.labelMov.setText(mov_details["name"])
        self.ui.labelGenre.setText(mov_details["genres"])
        self.ui.textMovSummary.setText(mov_details["plot"])
        self.ui.textDirector.setText(mov_details["directors"])
        self.ui.textProducer.setText(mov_details["producers"])
        self.ui.textStarCast.setText(mov_details["cast"])
        self.ui.textRTRating.setText(mov_details["rt_rating"])
        self.ui.textIMDBRating.setText(mov_details["imdb_rating"])
        self.ui.textVoteCount.setText(mov_details["votes"])
        self.displayImage(mov_details["img"])
        self.displayWordCloud(mov_details["plot"])
        self.emotionDisplay(mov)
        #self.displayReview(mov_details)
        if (len(mov_details["review"])):
            self.ui.review1.disconnect()
            self.ui.review1.clicked.connect(functools.partial(self.displayReview, mov_details))
        QCoreApplication.processEvents()
        #if(len(mov_details["reviews"])):
        #    self.displayRakeKeywords(mov_details["reviews"][0])
        #    self.displayTextRankKeywords(mov_details["reviews"][0])
        #    self.displayKeywords(mov_details["reviews"][0])

    def emotionDisplay(self,mov):
        path = mov_to_path(mov).split(".")[0]+".srt"
        print path
        try:
            emotions = predictEmo(path,self.emovecs)
        except Exception as e:
            print e.message
        if emotions is None:
            self.ui.pbarAngry.setValue(0)
            self.ui.pbarSurprise.setValue(0)
            self.ui.pbarFear.setValue(0)
            self.ui.pbarSad.setValue(0)
            self.ui.pbarHappy.setValue(0)
        print emotions
        self.ui.pbarAngry.setValue(emotions['anger']*100)
        self.ui.pbarSurprise.setValue(emotions['surprise']*100)
        self.ui.pbarFear.setValue(emotions['fear']*100)
        self.ui.pbarSad.setValue(emotions['sad']*100)
        self.ui.pbarHappy.setValue(emotions['happy']*100)

    def displayWordCloud(self, plot):
        #print plot
        rake = Rake("SmartStoplist.txt")
        keywords = rake.run(str(plot))
        #print keywords
        data = WordCloud(max_words=15).generate_from_frequencies(keywords)
        img = data.to_image()
        #print img
        pix = QtGui.QPixmap.fromImage(ImageQt(img))
        scaledPix = pix.scaled(self.ui.wordCloudLabel.size(), QtCore.Qt.KeepAspectRatio)

        #img.show()
        #data = img.tostring('raw', 'RGBA')
        #image = QtGui.QImage(data, img.size[0], img.size[1], QtGui.QImage.Format_ARGB32)
        #pix = QtGui.QPixmap.fromImage(image)

        self.ui.wordCloudLabel.setPixmap(scaledPix)
        #print "displayed"

    def displayReview(self, mov_details):
        print mov_details["name"]
        class MyWebView(QWebView):
            def __init__(self):
                QWebView.__init__(self)
                self.setWindowTitle(mov_details["name"])
                #print "Hello"

            def _loadFinished(self):
                js1 = """
                var text = "Less impressive are the screenplay and Ron Howard's direction";
                var re = new RegExp(text, "gi");
                document.body.innerHTML = document.body.innerHTML.replace(re,"<span style='color:blue'>" + text + "</span>");
                """

                js2 = """
                var text = {0};
                var re = new RegExp(text, "gi");
                document.body.innerHTML = document.body.innerHTML.replace(re,"<span style='color:{1}'>" + text + "</span>");
                """
                sentences = "Writer Akiva Goldsman (he of the two bad Batman films fame), adapting the script from Sylvia Nasar's biography of Nash, reveals only the warts that aren't too ugly (there is no mention of Nash's bisexuality or of his divorce from Alicia)."
                sentences = sentences.split(".")
                # print repr(sentences[0])
                # sentences[0] = sentences[0].replace("\n","")
                # sentences[0] = "\"%s.\"" % ( sentences[0] )
                # print repr(sentences[0])
                # js2 = js2.format(sentences[0], "red")
                #for sent in sentences:
                #    sent = sent.replace("\n","")
                #    sent = "\"%s.\"" % ( sent )
                #    print repr(sent)
                #    js2 = js2.format(sent, "red")


                #tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
                #tokens = [token.replace("\n", "") for token in tokenizer.tokenize(mov_details["reviews"][0])]
                #print tokens
                #for token in tokens:
                #    #print token
                #    js2 = js2.format(token, "blue")q
                #    self.page().mainFrame().evaluateJavaScript(js2)

                #print js2
                #print js2==js1
                #self.page().mainFrame().evaluateJavaScript(js2)
                #self.page().mainFrame().evaluateJavaScript("""alert("done")""")
                print "load finished"

        print "Review clicked "
        self.webview = MyWebView()
        #self.webview.load(QtCore.QUrl(mov_details["review_urls"][0]))
        html = str(mov_details["review"])
        html = self.sentimentify(html)
        self.webview.setHtml(html)
        path = os.getcwd()
        self.webview.settings().setUserStyleSheetUrl(QtCore.QUrl.fromLocalFile( path + "/review.css"))
        #self.webview.loadFinished.connect(self.webview._loadFinished)
        self.webview.show()

        ##Old Code to replace string
        """//var index = innerHTML.indexOf(text);
                //alert(index);
                //if(index >=0)
                    //innerHTML = innerHTML.substring(0,index) + "<span style='color:blue'>" + innerHTML.substring(index,index+text.length) + "</span>" + innerHTML.substring(index + text.length);"""

        #####Code to add CSS File
        #path = os.getcwd()
        #self.webview.settings().setUserStyleSheetUrl(QtCore.QUrl.fromLocalFile(path + "/highlight.css"))

    def sentimentify(self, review):
        rake = Rake("SmartStoplist.txt")
        keywords = rake.run(review)
        #print keywords
        data = WordCloud(max_words=15).generate_from_frequencies(keywords)
        img = data.to_image()
        output = StringIO.StringIO()
        img.save(output, format = 'PNG')
        output.seek(0)
        output_s = output.read()
        b64 = base64.b64encode(output_s)

        strRev = '<img src="data:image/png;base64,{0}"/>'.format(b64)
        review_sentences = nltk.sent_tokenize(review)
        scores = test(review_sentences)
        # test(reviews[0])
        colors = [ '#FF0000', '#FF9900', '#FFFF66', '#CCFFBB', '#005A04' ]

        for score,review_sentence in zip(scores,review_sentences):
            strRev += "<span style='background-color:{0}'>".format(colors[score]) + review_sentence + " " + "</span>"

        strRev = "<html><body><p>" + strRev + "</p></body></html>"
        print strRev
        return strRev

    def displayRakeKeywords(self, review):
        rake = Rake("SmartStoplist.txt")
        keywords = rake.run(str(review))
        print keywords
        text = ""
        for word in keywords[:10]:
            text += str(word[0])
            text += ";\n"
        #self.ui.keywordLabel.setText(text)
        #self.ui.keywordLabel.setToolTip(text)

    def displayTextRankKeywords(self, review):
        review = review.decode('utf8')
        keywords = extractKeyphrases(review)
        print keywords
        keywords = list(keywords)
        text = ""
        for word in keywords[:10]:
            text += str(word)
            text += ";\n"
        #self.ui.keywordLabel_2.setText(text)
        #self.ui.keywordLabel_2.setToolTip(text)

    def displayKeywords(self, review):
        review = review.decode('utf8')
        wordTokens = nltk.word_tokenize(review)
        tagged = nltk.pos_tag(wordTokens)
        #textlist = [x[0] for x in tagged]
        tags = ['JJ']
        adjectives = [item[0] for item in tagged if item[1] in tags]
        print set(adjectives)


    #it does not overwrite the db, rather inserts duplicate values
    #correct it
    def internet_sync_trigger(self):
        self.syncer = MovieSyncThread(self)
        self.syncer.startSignal.connect(self.init_progressbar)
        self.syncer.updateSignal.connect(self.update_progressbar)
        self.syncer.terminateSignal.connect(self.terminate_progressbar)
        self.syncer.start()

    def terminate_progressbar(self):
        self.ui.progressInfo.setVisible(False)
        self.ui.progressBar.setVisible(False)

    def update_progressbar(self):
        self.ui.progressBar.setValue(self.ui.progressBar.value() + 1)

    def init_progressbar(self, maxProgressBarValue):
        print "Initialize progress bar now"
        # self.ui.progressInfo.setVisible(True)
        self.ui.progressBar.setVisible(True)
        self.ui.progressBar.setMaximum(maxProgressBarValue)
        # self.ui.progressInfo.setText("Fetching info...Please Wait!")
        self.ui.statusbar.showMessage("Fetching info...Please Wait!")
        self.ui.progressBar.setValue(0)

    def recommendMovies(self):
        list = getSeenMovies()
        reco_thread = RecommenderThread(self,15,list)
        reco_thread.startSignal.connect(self.init_progressbar)
        reco_thread.updateSignal.connect(self.update_progressbar)
        reco_thread.terminateSignal.connect(self.terminate_recos)
        reco_thread.start()

    def terminate_recos(self,recos):
        seen_movies = getSeenMovies()
        seen_movie_longnames = [name for id,imdb_id,name in seen_movies]
        for movie in recos:
            if movie["long imdb canonical title"] not in seen_movie_longnames:
                self.ui.listWidgetRecommend.addItem(movie['title'])
        self.terminate_progressbar()	

class MovieSyncThread(QtCore.QThread):

    startSignal = QtCore.pyqtSignal(int)
    updateSignal = QtCore.pyqtSignal()
    terminateSignal = QtCore.pyqtSignal()

    def __init__(self,parent):
        QtCore.QThread.__init__(self,parent)

    def run(self):
        mov_names = get_mov_names()
        self.startSignal.emit(len(mov_names))

        print "Performing Sync"
        if check_net() is True:
            for mov in mov_names:
                # self.parent.ui.progressBar.setValue(init_value)
                add_mov_details_to_db(mov)
                self.updateSignal.emit()
        self.terminateSignal.emit()
            # Parallel(n_jobs=-1,verbose=2,backend="threading")(
            #     delayed(add_mov_details_to_db)(mov) for mov in mov_names)
        # self.parent.ui.progressInfo.setVisible(False)
        # self.parent.ui.progressBar.setVisible(False)

class RecommenderThread(QtCore.QThread):
    startSignal = QtCore.pyqtSignal(int)
    updateSignal = QtCore.pyqtSignal()
    terminateSignal = QtCore.pyqtSignal(list)

    def __init__(self,parent,n,movies_lst):
        QtCore.QThread.__init__(self,parent)
        self.n = n
        self.movies_lst = movies_lst

    def run(self):
        self.startSignal.emit(1)
        print "Generating Recommendations"
        recos_list = Recommender().get_n_recommendations(self.n,self.movies_lst)
        self.updateSignal.emit()
        self.terminateSignal.emit(recos_list)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("fusion")
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    window = MyApp()
    #window.showMaximized()
    window.show()
    sys.exit(app.exec_())