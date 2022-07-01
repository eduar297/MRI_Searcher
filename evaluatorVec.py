import os
import directory
from Model_Vectorial import Vectorial

def get_queries(path):
    from_id_to_query = {}
    current_query_text = ''
    current_query_id = 0
    with open(path) as fp:
        for _,line in enumerate(fp):
            if line[:2] == '.I':
                if current_query_id != 0:
                    from_id_to_query[current_query_id] = current_query_text
                current_query_text = ''
                current_query_id = int(line[3:])
            elif line[:2] == '.W':
                continue
            else:
                # add line to current_document_text
                current_query_text += line[:-1] + ' '
        # add the last query
        from_id_to_query[current_query_id] = current_query_text

    return from_id_to_query

def get_relevant_sets(path):
    relevant_sets = []
    with open(path) as fp:
        for _,line in enumerate(fp):
            line = line.split()
            q_id, doc_id, code = int(line[0]), int(line[1]), int(line[2])
            if q_id > len(relevant_sets):
                relevant_sets.append(set())
            if code > 0 and code < 4:
                relevant_sets[q_id-1].add(doc_id)

    return relevant_sets

def f_measurement(precision, recovered, beta=0.5):
    if recovered == 0:
        return 0
    if precision == 0:
        return 0
    return (1 + beta**2) / (1/precision + beta**2/recovered)

class Evaluator:
    def __init__(self, path_query, path_rel, path_collection):
        self.path_collection = path_collection
        self.from_id_to_query = get_queries(path_query)
        self.relevant_sets = get_relevant_sets(path_rel)
        #------------Code to handle irModel--------------------
        self.irModel = Vectorial(path_collection)

    def get_queries(self):
        return self.from_id_to_query.items()

    def evaluate_system(self, queries):
        '''
        :param queries: a list of int representing queries ids
        '''
        from_query_to_docs = {}
        for query_id in queries:
            query_id = int(query_id)
            query = self.from_id_to_query[query_id]
            relevant_documents = self.irModel.process_query(query)
            from_query_to_docs[query_id] = [int(doc[1].split('.')[0]) for doc in relevant_documents]

        return self.evaluate_queries(from_query_to_docs)

    def evaluate_queries(self, from_query_to_docs):
        '''
        :param from_query_to_docs: is a dictionary from query_id to list of doc_id 
        '''

        def r_precision(q_id, R=None):
            docs = from_query_to_docs[q_id]
            if R:
                docs = docs[:R]
            rr = sum([1 for doc_id in docs if doc_id in self.relevant_sets[q_id-1]])
            return rr/R

        p_list = []
        r_list = []
        f_list = []
        f1_list = []
        rp_lis = []
        for query_id,docs in from_query_to_docs.items():
            rr = sum([1 for doc_id in docs if doc_id in self.relevant_sets[query_id-1]])
            p = rr/len(docs) if len(docs) != 0 else 0

            if self.path_collection == 'collection/cran/docs':
                r = rr/len(self.relevant_sets[query_id-1]) if len(self.relevant_sets[query_id-1]) != 0 else 0
            else:
                r = rr/len(self.relevant_sets[query_id-1]) if len(self.relevant_sets[query_id-1]) != 0 else 1


            p_list.append(p)
            r_list.append(r)
            f_list.append(f_measurement(p, r))
            f1_list.append(f_measurement(p, r, beta=1))
            rp_lis.append(r_precision(query_id, R=10))
        
        # return a tuple (presicion, recovered, f_measure, f1_measure, r-precision) with the average for every measure for all the queries
        return sum(p_list)/len(p_list), sum(r_list)/len(r_list), sum(f_list)/len(f_list), sum(f1_list)/len(f1_list), sum(rp_lis)/len(rp_lis)

if __name__ == '__main__':
    es_cran = Evaluator('cran\cran.qry', 'cran\cranqrel', 'collection/cran/docs')
    print(es_cran.evaluate_system([1, 2, 4, 8, 9, 10, 12, 13, 15, 18, 22, 23, 26, 27, 29, 31, 32, 33, 34, 35, 39, 40, 41, 49, 50]))

    es_cisi = Evaluator('cisi\CISI.QRY', 'cisi\CISI.REL', 'collection/cisi/docs')
    print(es_cisi.evaluate_system([1, 2, 4, 8, 9, 10, 12, 13, 15, 18, 22, 23, 26, 27, 29, 31, 32, 33, 34, 35, 39, 40, 41, 49, 50]))