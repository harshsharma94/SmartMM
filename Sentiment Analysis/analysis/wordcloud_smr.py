from utilities import load_data,DataClean
import matplotlib.pyplot as plt
from wordcloud import WordCloud

def generate_wordcloud(joined_sentences,label,dset,bg_color):
    wordcloud = WordCloud(font_path="./CabinSketch-Bold.ttf",
                          background_color=bg_color,
                          width=1800,
                          height=1400).generate(joined_sentences)
    plt.imshow(wordcloud)
    plt.axis('off')
    plt.savefig('wordcloud_{}_{}_{}'.format(dset,label,bg_color), dpi=400)

def run_analysis(dset):
    ids,X,y = load_data(dset)
    X = DataClean([["[^a-z]"," "],
                   [" [ ]+", " "],],html_clean=True).fit(X).transform(X)
    labels = list(set(y))
    for label in labels:
        Xlabel = X[y==label]
        Xlabel_str = ' '.join(Xlabel.tolist())
        generate_wordcloud(Xlabel_str,label,dset,"white")
        generate_wordcloud(Xlabel_str,label,dset,"black")
        print "Label %d : %s" % (label,Xlabel[0])



if __name__ == '__main__':
    run_analysis("stanford")
    run_analysis("cornell")

