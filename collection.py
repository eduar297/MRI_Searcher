
import os

def save_cran_doc(id, text, title):
    with open(f'collection/cran/titles/{id}.txt', 'w') as d:
        d.writelines(title)
    with open(f'collection/cran/docs/{id}.txt', 'w') as f:
        f.write(text)
        
def save_cisi_doc(id, text, title):
    with open(f'collection/cisi/titles/{id}.txt', 'w') as d:
        d.writelines(title)
    with open(f'collection/cisi/docs/{id}.txt', 'w') as f:
        f.write(text)


def build_cran_documents():
    # create /collection directory
    if not os.path.exists('collection/cran'):
        os.mkdir('collection/cran')
        
        os.mkdir('collection/cran/docs')
        os.mkdir('collection/cran/titles')

        current_doc_title = ''
        current_doc_text = ''
        current_doc_id = 0
        title = 0
        text = 0
        with open('cran\cran.all.1400') as fp:
            for _,line in enumerate(fp):
                if line[:2] == '.I':
                    title = 0
                    text = 0
                    if current_doc_id != 0:
                        save_cran_doc(current_doc_id, current_doc_text, current_doc_title)
                    current_doc_text = ''
                    current_doc_title = ''
                    current_doc_id = int(line[3:])

                elif line[:2] in {'.A','.B'}:
                    text = 0
                    title = 0
                    continue

                if line[:2] == '.T':
                    title = 1
                    text = 0
                    continue

                if line[:2] == '.W':
                    title = 0
                    text = 1
                    continue

                else:
                    # add line to current_document_text
                    if title:
                        current_doc_title += line[:-1] + ' '
                    elif text:
                        current_doc_text += line[:-1] + ' '
            # add document 1400
            save_cran_doc(current_doc_id, current_doc_text, current_doc_title)

def build_cisi_documents():
    # create /collection directory
    if not os.path.exists('collection/cisi'):        
        os.mkdir('collection/cisi')
        
        os.mkdir('collection/cisi/docs')
        os.mkdir('collection/cisi/titles')

        current_doc_title = ''
        current_doc_text = ''
        current_doc_id = 0
        title = 0
        text = 0
        with open('cisi\CISI.ALL') as fp:
            for _,line in enumerate(fp):
                if line[:2] == '.I':
                    title = 0
                    text = 0
                    if current_doc_id != 0:
                        save_cisi_doc(current_doc_id, current_doc_text, current_doc_title)
                    current_doc_text = ''
                    current_doc_title = ''
                    current_doc_id = int(line[3:])

                elif line[:2] in {'.A','.X'}:
                    text = 0
                    title = 0
                    continue

                if line[:2] == '.T':
                    title = 1
                    text = 0
                    continue

                if line[:2] == '.W':
                    title = 0
                    text = 1
                    continue

                else:
                    # add line to current_document_text
                    if title:
                        current_doc_title += line[:-1] + ' '
                    elif text:
                        current_doc_text += line[:-1] + ' '
            # add document 1400
            save_cisi_doc(current_doc_id, current_doc_text, current_doc_title)


def build_cran_queries():
    # create /collection directory
    if not os.path.exists('collection'):
        os.mkdir('collection')

    from_id_to_query = {}
    current_query_text = ''
    current_query_id = 0
    with open('cran\cran.qry') as fp:
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
    
    # # save the query set into a pickle file
    # with open('collection\queries.file', 'wb') as f:
    #     pickle.dump(from_id_to_query, f, pickle.HIGHEST_PROTOCOL)

    return from_id_to_query


if __name__ == '__main__':
    build_cran_documents()
    build_cisi_documents()