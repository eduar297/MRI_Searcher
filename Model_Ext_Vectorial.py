from Model import Model

from Ext.jsonUtils import Utils
import numpy as np
from numpy import dot
from numpy.linalg import norm
import os
import directory

RELEV_COEF = 0.3
NUM_REC = 140
#Receive an iterable of docs
class Ext_Vectorial(Model):
    
    def __init__(self, _directory):
        super().__init__(_directory)
        self.doc_names = {} #dict of num_doc -> url
        self.docs_to_term = {} #dict of term->[documents] where term appear (documents is an Int)
        self.index_of_term = {} #term -> int the index of the given term
        self.termVec = []
        self.docVec = []
        self.w = []
        self.num_docs = 0
        self.makeFolders()

        try:
            lastBuild = Utils.get_json_as_dict('docs_in_call')
        except:
            lastBuild = []

        newBuild = directory.get_interested_files(self.directory)
        Utils.save_as_json(newBuild,'docs_in_call')

        if lastBuild != newBuild:
            print('Building indexes...')
            self.process_documents(directory.list_directory(self.directory, True))
            self.buildIndexes()
            self.save_documents_state() 
        else:
            print('Loading indexes...')
            self.get_document_state()

    #docs in an iterable of [Documents]
    def process_documents(self,docs):

        for doc in docs:            
            tf = {} #dict of term->freq    
            maxTf = 0 
            self.num_docs += 1    
            self.doc_names[str(self.num_docs-1)] = doc[0]
            terms = list(doc[1][0])
            for term in terms:
                if not term in self.docs_to_term: #is a new Term
                    self.docs_to_term[term] = [self.num_docs-1]
                    self.index_of_term[term] = len(self.docs_to_term)-1
                elif (self.num_docs-1) not in self.docs_to_term[term]: #is a new document where term appear
                    self.docs_to_term[term].append(self.num_docs-1)
                if not term in tf:
                    tf[term] = 1
                else:
                    tf[term] += 1
                if tf[term] > maxTf:
                    maxTf = tf[term]
            for term in tf.keys():
                tf[term] /= maxTf            
            self.w.append(tf)
        self.correlations = self.save_corr_matrix()

    #save correlation matrix as a list of Rows of Json
    def save_corr_matrix(self):
        i = 0
        matr = []
        for term in self.docs_to_term:
            i+=1
            n_i = set(self.docs_to_term[term])
            term_corr = []
            for j in self.docs_to_term:
                n_j = set(self.docs_to_term[j])
                commun = len(n_i&n_j)
                term_corr.append(commun/(len(n_i)+len(n_j)-commun))
            matr.append(term_corr)
        return matr

    #build and save terms vectors and document vectors 
    def buildIndexes(self):
        active_minterms = {}
        minterm_order = {}

        for i in range(self.num_docs):
            vector = np.zeros(len(self.docs_to_term))
            tf = self.w[i]
            for term in tf:  
                vector[self.index_of_term[term]] = 1
            vector = tuple(vector)
            if vector not in active_minterms:
                active_minterms[vector] = [i]
                minterm_order[vector] = len(active_minterms)
            else:
                active_minterms[vector].append(i) 

        for term in self.docs_to_term:   
            vector = np.zeros(len(active_minterms))
            for minterm,list_of_docs in active_minterms.items():
                if minterm[self.index_of_term[term]]:
                    C_ir = 0
                    for doc in list_of_docs:
                        tf = self.w[doc]
                        C_ir += tf[term]*np.log((self.num_docs+1)/(len(self.docs_to_term[term])+1))
                    vector[minterm_order[minterm]-1] += C_ir

            _norm = norm(vector)
            vector = vector/_norm if _norm > 0 else vector
            self.termVec.append(list(vector))

        for i in range(self.num_docs):
            vector = np.zeros(len(active_minterms))
            tf = self.w[i]
            for term in tf:     #foreach term in doc
                w_ij = tf[term]*np.log((self.num_docs+1)/(len(self.docs_to_term[term])+1))
                term_vector = np.array(self.termVec[self.index_of_term[term]])
                vector += (w_ij*term_vector)
            self.docVec.append(list(vector))
    
    #query is a [terms]
    def process_query(self,query):
        relevant_docs = []
        query_vector = np.zeros(len(self.docVec[0]))
        query_term_cost = {}
        query_term_freq = {}
        max_query_freq = 0

        for term in query: #process query terms
            if term not in query_term_freq:
                query_term_freq[term] = 1
            else:
                query_term_freq[term] += 1
            _aux = query_term_freq[term]
            if _aux > max_query_freq:
                max_query_freq = _aux

        for term in self.docs_to_term: #make query's vector
            query_term_cost[term] = ((0.5 + (0.5*query_term_freq[term])/max_query_freq)*np.log((self.num_docs+1)/(len(self.docs_to_term[term])+1))) if term in query_term_freq else 0

        list_of_terms = list(self.docs_to_term.keys())
        for i in range(len(list_of_terms)):
            term = list_of_terms[i-1]
            cost = query_term_cost[term] if term in query_term_cost else 0
            # term_vec = np.array(self.termVec[i])
            query_vector += (cost*np.array(self.termVec[i]))
            # for j in range(len(query_vector)):
            #     query_vector[j] += cost*term_vec[j]        

        Utils.save_as_json(list(query_vector),'queryVector')
        for i in range(self.num_docs):
            corr = dot(self.docVec[i],query_vector) / (norm(self.docVec[i])*norm(query_vector))     
            if corr > RELEV_COEF:                
                relevant_docs.append((corr, self.doc_names[str(i)]))
        return sorted(relevant_docs,reverse=True)[:NUM_REC]
        
    def save_documents_state(self):
        Utils.save_as_json(self.doc_names,'doc_names')
        Utils.save_as_json(self.docs_to_term,'docs_to_term')
        Utils.save_as_json(self.index_of_term,'index_of_term')
        Utils.save_as_json(self.correlations,'correlations') #new
        Utils.save_as_json(list(self.docVec),'docVects')
        Utils.save_as_json(list(self.termVec),'termVectors')

    #Ensure that exist preprocessed documents
    def get_document_state(self):
        if self.docs_to_term == {}:
            try:
                self.docs_to_term = Utils.get_json_as_dict('docs_to_term')
                self.doc_names = Utils.get_json_as_dict('doc_names')
                self.num_docs = len(self.doc_names)
                self.index_of_term = Utils.get_json_as_dict('index_of_term')
                self.docVec = Utils.get_json_as_dict('docVects')
                self.termVec = Utils.get_json_as_dict('termVectors')
                self.correlations = Utils.get_json_as_dict('correlations')
            except:
                print('An error ocurred while loading Jsons')
                raise
    
    #Ensure exist some important folders
    def makeFolders(self):
        try:
            os.mkdir("Jsons")
        except:
            pass