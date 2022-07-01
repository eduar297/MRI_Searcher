import re
import unicodedata
import nltk
import contractions
import inflect
from bs4 import BeautifulSoup
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import LancasterStemmer, WordNetLemmatizer


def strip_html(text):
    """Remove html markup."""
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text()


def remove_between_square_brackets(text):
    """Remove open and close double brackets and anything in between."""
    return re.sub('\[[^]]*\]', '', text)


def denoise_text(text):
    text = strip_html(text)
    text = remove_between_square_brackets(text)
    return text


def replace_contractions(text):
    """Replace contractions in string of text."""
    return contractions.fix(text)


def get_tokenized_list(doc_text):
    tokens = word_tokenize(doc_text)
    return tokens


def remove_non_ascii(words):
    """Remove non-ASCII characters from list of tokenized words"""
    new_words = []
    for word in words:
        new_word = unicodedata.normalize('NFKD', word).encode(
            'ascii', 'ignore').decode('utf-8', 'ignore')
        new_words.append(new_word)
    return new_words


def to_lowercase(words):
    """Convert all characters to lowercase from list of tokenized words"""
    new_words = []
    for word in words:
        new_word = word.lower()
        new_words.append(new_word)
    return new_words


def remove_punctuation(words):
    """Remove punctuation from list of tokenized words"""
    new_words = []
    for word in words:
        new_word = re.sub(r'[^\w\s]', '', word)
        if new_word != '':
            new_words.append(new_word)
    return new_words


def replace_numbers(words):
    """Replace all interger occurrences in list of tokenized words with textual representation"""
    p = inflect.engine()
    new_words = []
    for word in words:
        if word.isdigit():
            new_word = p.number_to_words(word)
            new_words.append(new_word)
        else:
            new_words.append(word)
    return new_words


def remove_stopwords(words, language):
    """Remove stop words from list of tokenized words"""
    stop_words = set(stopwords.words(language))
    new_words = []
    for word in words:
        if word not in stop_words:
            new_words.append(word)
    return new_words


def stem_words(words):
    """Stem words in list of tokenized words"""
    stemmer = LancasterStemmer()
    stems = []
    for word in words:
        stem = stemmer.stem(word)
        stems.append(stem)
    return stems


# def stem_words_1(words):
#     ps = nltk.stem.PorterStemmer()
#     stems = []
#     for word in words:
#         stems.append(ps.stem(word))
#     return stems


def lemmatize_words(words):
    """Lemmatize words in list of tokenized words"""
    lemmatizer = WordNetLemmatizer()
    lemmas = []
    for word in words:
        lemma = lemmatizer.lemmatize(word, pos='n')
        lemma = lemmatizer.lemmatize(lemma, pos='v')
        lemma = lemmatizer.lemmatize(lemma, pos='a')
        lemma = lemmatizer.lemmatize(lemma, pos='r')
        lemma = lemmatizer.lemmatize(lemma, pos='s')
        lemmas.append(lemma)
    return lemmas


def normalize(words, normalization_type, language):
    words = remove_non_ascii(words)
    words = to_lowercase(words)
    words = remove_punctuation(words)
    words = replace_numbers(words)
    words = remove_stopwords(words, language)

    if(normalization_type == 'stems'):
        return stem_words(words)

    elif(normalization_type == 'lemmas'):
        return lemmatize_words(words)

    elif(normalization_type == 'lemmas and stems'):
        return stem_and_lemmatize(words)

    elif(normalization_type == 'none'):
        return words

    else:
        return words


def stem_and_lemmatize(words):
    lemmas = lemmatize_words(words)
    stems = stem_words(lemmas)
    return stems


def preprocess_text(text, normalization_type, text_type, language):
    pt = text
    if text_type == 'html':
        pt = denoise_text(text)

    pt = replace_contractions(pt)
    words = get_tokenized_list(pt)
    words = normalize(words, normalization_type, language)
    return words
