import os

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from Model import Model
import directory
from Vector.text_preprocessor import preprocess_text


class Vectorial(Model):
    def __init__(self, _directory, normalization_type='lemmas and stems', language='english'):
        super().__init__(_directory)
        self.normalization_type = normalization_type
        self.language = language
        self.doc_names = {}  # dict of num_doc -> url
        self.doc_vector = []  # Wij
        self.corpus = []
        self.cleaned_corpus = []
        self.num_docs = 0
        self.terms = []
        
        self.process_documents(directory.list_directory(self.directory))

    def process_documents(self, docs):

        for doc in docs:             

            self.num_docs += 1
            self.doc_names[str(self.num_docs-1)] = doc[0]
            doc_text = doc[1]
            self.corpus.append(doc_text)
            pt = preprocess_text(
                text=doc_text, normalization_type=self.normalization_type, text_type='txt', language=self.language)
            pt = ' '.join(pt)
            self.cleaned_corpus.append(pt)

        vectorizerX = TfidfVectorizer()
        vectorizerX.fit(self.cleaned_corpus)
        doc_vector = vectorizerX.transform(self.cleaned_corpus)
        self.doc_vector = doc_vector

        self.vectorizerX = vectorizerX

        self.find_all_indexed_terms()

    def find_all_indexed_terms(self):
        terms = set()
        for _doc in self.cleaned_corpus:
            doc = _doc.split()
            for t in doc:
                terms.add(t)
        terms = set(terms)
        terms = list(terms)
        terms = sorted(terms)
        self.terms = terms

    def process_query(self, query):
        pq = preprocess_text(text=query, normalization_type=self.normalization_type,
                             text_type='txt', language=self.language)
        pq = ' '.join(pq)

        query_vector = self.vectorizerX.transform([pq])

        cosineSimilarities = cosine_similarity(
            self.doc_vector, query_vector).flatten()

        related_docs_indices = cosineSimilarities.argsort()[::-1]
        # print(related_docs_indices)

        relevant_docs = []
        for i in related_docs_indices:
            data = [self.corpus[i]]
            cos = cosineSimilarities[i]
            if cos > 0.3:
                # print(f'cos:{cos}  data: {data}')
                relevant_docs.append((cos, self.doc_names[str(i)]))
                # relevant_docs.append((self.doc_names[str(i)], data))

        return relevant_docs