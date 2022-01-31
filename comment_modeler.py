import numpy as np
import pandas as pd
import gensim
import re
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from pprint import pprint
from sklearn.feature_extraction.text import CountVectorizer
import matplotlib.pyplot as plt
from ipywidgets import interact, IntSlider


def create_comment_model():
    #import data
    comments = pd.read_csv('data/comments.csv')[['comments']].dropna().drop_duplicates()

    # vectorize words for gensim
    vectorizer = CountVectorizer(ngram_range=(2,3),
                             stop_words=STOP_WORDS.union({'ll', 've', 'pron',
                                                                'good','great', 'nice',
                                                                'ride','route','road','rt','roads'
                                                               }),
                            )
    analyzer = vectorizer.build_analyzer()


    texts = comments.comments.values.tolist()
    processed_text = [analyzer(text) for text in texts]
    dictionary = gensim.corpora.Dictionary(processed_text)
    corpus = [dictionary.doc2bow(t) for t in processed_text]

    #LDA model parameters
    num_topics = 4
    lda_model = gensim.models.ldamodel.LdaModel(corpus=corpus,
                                            id2word=dictionary,
                                            num_topics=num_topics,
                                            random_state=17, update_every=1,
                                            chunksize=1500,
                                            passes=5, iterations=10,
                                            alpha='asymmetric', eta=1/100,
                                            per_word_topics=True)
    return lda_model, dictionary, corpus, processed_text



def get_main_topic_df(model, bow, texts):
    '''extracts dominant topic (and percentage) for each comment'''
    topic_list = []
    percent_list = []
    keyword_list = []

    for wc in bow:
        topic, percent = sorted(model.get_document_topics(wc), key=lambda x: x[1], reverse=True)[0]
        topic_list.append(topic)
        percent_list.append(round(percent, 3))
        keyword_list.append(' '.join(sorted([x[0] for x in model.show_topic(topic)])))

    result_df = pd.concat([pd.Series(topic_list, name='Dominant_topic'),
                           pd.Series(percent_list, name='Percent'),
                           pd.Series(texts, name='Processed_text'),
                           pd.Series(keyword_list, name='Keywords')], axis=1)

    return result_df
