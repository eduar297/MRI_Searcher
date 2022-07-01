'''
All the text processed in this module is in txt-utf8
format 
'''

import re
import nltk
from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn
from nltk.stem import PorterStemmer, WordNetLemmatizer
from Ext.jsonUtils import Utils

## Document Processing(text operations):
# 1- Lexical analysis of the text with the objective of treating digits, 
#    hyphens, punctuation marks, and the case of letters.
# 2- Elimination of stopwords with the objective of filtering out words 
#    with very low discrimination values for retrieval purposes.
# 3- Stemming of the remaining words with the objective of removing affixes
#    (i.e., prefixes and suffixes) and allowing the retrieval of documents 
#    containing syntactic variations of query terms (e.g., connect, connecting, connected, etc).

# sentences tokenizer
sent_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
# words tokenizer
word_tokenizer = nltk.tokenize.WordPunctTokenizer()
# words stemmer
word_stemmer = PorterStemmer()
# word lemmatizer
word_lemmatizer = WordNetLemmatizer()
# english stopwords
english_stops = set(stopwords.words('english'))
# Part of speech tagging
relevant_tags = {
        'JJ','JJR','JJS',
        'FW',
        'NN','NNP','NNPS','NNS',
        'VB','VBD','VBG','VBN','VBP','VBZ'}
map_tags = {
    'JJ':'a','JJR':'a','JJS':'a',
    'NN':'n','NNP':'n','NNPS':'n','NNS':'n',
    'VB':'v','VBD':'v','VBG':'v','VBN':'v','VBP':'v','VBZ':'v'}

def query_porcessing(query, term_to_index, corrMatrix,threshold=0.5):
    '''
    :param query: type str
    :param correlation_matrix: is a matrix of txt of floats
    :param text_to_index: is is a dict from str_term to int_index
    '''
    a, b = text_processing(query)
    gen_proc_words, gen_tag_words = list(a), list(b)
    expanded_query = gen_proc_words.copy()
    index = 0
    for word,tag in gen_tag_words:
        pos = map_tags.get(tag,'n')
        expanded_words = set()
        for syns in wn.synsets(word, pos=pos):
            for syn in syns.lemma_names():
                # lemmatize the synonym
                syn = word_lemmatizer.lemmatize(syn, pos=pos)
                # stemmize the synonym
                syn = word_stemmer.stem(syn)

                # expanded_words.add((syn, pos)) # delete this line of code

                # check if the synonym is suitable for query expansion
                if syn in term_to_index.keys() and gen_proc_words[index] in term_to_index.keys():
                    word_id = term_to_index[gen_proc_words[index]]
                    syn_id = term_to_index[syn]
                    if corrMatrix[word_id][syn_id] > threshold:
                        if (syn, pos) not in expanded_words:
                            expanded_words.add((syn, pos))

        expanded_query.extend([w for w,_ in expanded_words])
        index += 1
    
    return (w for w in expanded_query)

def text_processing(text):
    ################################################
    ## Lexical Analysis                           ## 
    ################################################
    # Cases to care about:
    # 1- Digits(remove all numbers)
    # 2- Hyphens(separate the words)
    # 3- Punctuation Marks(remove all of them)
    # 4- Case of the letters(convert to lowercase)

    # Sentence Spliting
    sentences = sent_tokenizer.tokenize(text)
    # Word Spliting
    word_sentences = (word_tokenizer.tokenize(sent) for sent in sentences)
    # Part-of-speech Tagging
    _tagged_sentences = nltk.pos_tag_sents(word_sentences)
    tagged_sentences = (word_tag for sent in _tagged_sentences for word_tag in sent)
    # Analize every word in the text acoording its tag(remove all numbers)
    lexical_words = filter((lambda word_tag: word_tag[1] in relevant_tags), tagged_sentences)
    # remove the punctuation marks
    without_punct_words = ((re.sub(r'[^\w\s]','', word),tag) for word,tag in lexical_words if re.sub(r'[^\w\s]','', word))

    ################################################
    ## Elimination of Stopwords                   ## 
    ################################################
    without_stops_words = list(filter((lambda word_tag: not word_tag[0] in english_stops), without_punct_words))

    ################################################
    ## Lemmatization                              ## 
    ################################################
    lemm_words = (word_lemmatizer.lemmatize(word, pos=map_tags.get(tag,'n')) for word,tag in without_stops_words)

    ################################################
    ## Stemming                                   ## 
    ################################################
    # also convert all words to lowercase 
    stem_words = map(word_stemmer.stem, lemm_words)

    return stem_words, (item for item in without_stops_words)


if __name__ == '__main__':    
#     text = '''
#     The house behind home 454 is not empty any more. Michael a joyful-person who loves to make big 
# parties at weekends, is living there now. He is very helpful and honest, these are the qualities
# that I'll like from him the most and that makes can't him the best suitable man to take care of my bills 
# when I am away from home. His parties, on 56456 the other hand, are another story. They are very noisy
# and the street is full of cars, so it makes that drive my car at weekends becomes a problem. So 
# as you see the perfect neighbor doesn't exist.
# '''

#     query = 'Michael a joyful-person who loves to make big parties at weekends.'
    
#     a, b = text_processing(query)
#     a, b = list(a), list(b)
#     print(a)
#     print(b)
    
# #     print(query_porcessing(query))
    pass