from vector_dict.VectorDict import Path, VectorDict, iter_object, tree_from_path, convert_tree
v = { 'a' : { 'a' : { 'b' : 1 } } } 
w = VectorDict()
w.add_path( [ 'a', 'a', "c", 5 ] )
# OUT: defaultdict(<class 'vector_dict.VectorDict.VectorDict'>, {'a': defaultdict(<class 'vector_dict.VectorDict.VectorDict'>, {'a': defaultdict(<class 'vector_dict.VectorDict.VectorDict'>, {'b': 1})})}) ('a', 'a', 'c', 5)
print "???"
w.pprint()
# OUT: u'a->a->b'=1
