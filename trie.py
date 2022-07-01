import directory
from Vector.text_preprocessor import *

class Node( object ):
	def __init__( self, end_node = False ):
		self.end_node = end_node
		self.prefix_count = 0
		self.children = {}

class Trie( object ):
    def __init__( self, _directory ):
        self.root = Node()
        docs = directory.list_directory(_directory)
        corpus = []
        for doc in docs:
            pt = doc[1]
            pt = replace_contractions(pt)
            words = get_tokenized_list(pt)
            words = remove_non_ascii(words)
            words = to_lowercase(words)
            words = remove_punctuation(words)
            words = replace_numbers(words)
            words = remove_stopwords(words, 'english')
            
            corpus.append(words)
        
        for s in corpus:
            for w in s:
                self.insert(w)               
        
    
    def insert( self, key ):
        current = self.root
        for k in key:
        	if k not in current.children:
        		current.children[k] = Node()
        	current = current.children[k]
        	current.prefix_count += 1
        current.end_node = True
    
    def search( self, key ):
        current = self.root
        for k in key:
            if k not in current.children:
                return False
            current = current.children[k]
        return current.end_node
    
    def count( self, key ):
        current = self.root
        for k in key:
        	if k not in current.children:
        		return 0
        	current = current.children[k]
        return current.prefix_count
    
    def _walk( self, root, prefix ):
        out = []
        if root.end_node:
        	out.append( prefix )

        for ch in root.children:
        	if isinstance( prefix, tuple ):
        		tmp = self._walk( root.children[ch], prefix + (ch,) )
        	elif isinstance( prefix, list ):
        		tmp = self._walk( root.children[ch], prefix + [ch] )
        	else:
        		tmp = self._walk( root.children[ch], prefix + ch )
        	out.extend( tmp )
        return out
    
    def enumerate( self, key ):
        current = self.root
        for k in key:
        	if k not in current.children:
        		return []
        	current = current.children[k]

        return self._walk( current, key )	

# db = Trie()

# db.insert( "apple" )
# db.insert( "apples" )
# db.insert( "abanana" )
# db.insert( "applet" )

# print(db.enumerate( "a" ))
