'''
This module receives a path of a diretory to work. It also 
handles all the .txt and .pdf documents in this directory 
by converting them to format txt-utf8. The function 
list_directory return an iterator of strings where each 
string represents the text of some document in txt-utf8 format.   
'''
import os
from format_handling import extract_text_from_txt, extract_text_from_pdf
from Ext.text_processing import text_processing


def file_extension(filename):
    return filename.split('.')[-1]


def extract_text(path, filename):
    ext = file_extension(filename)
    if ext == 'txt':
        text = extract_text_from_txt(path+'\\'+filename)
    elif ext == 'pdf':
        text = extract_text_from_pdf(path+'\\'+filename)
    else:
        raise Exception('Format not allowed by the system.')

    return text

def get_interested_files(basepath):
    return list(entry for entry in os.listdir(basepath) if os.path.isfile(os.path.join(basepath, entry)) and file_extension(entry) in {'txt','pdf'})


def list_directory(basepath, ext=False):
    # N: number of document that have extension .txt or .pdf
    files = (entry for entry in os.listdir(basepath) if os.path.isfile(
        os.path.join(basepath, entry)) and file_extension(entry) in {'txt', 'pdf'})
    for doc in files:
        if ext:
            yield (doc , text_processing(extract_text(basepath, doc)))
        else:
            yield (doc, extract_text(basepath, doc))
