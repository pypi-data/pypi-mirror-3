#!/usr/bin/python
# -*- coding: utf-8 -*-
#WTFPL
"""Trying lame cosinus on text
to create the mysoginie and troll input text file
you need *nix 
fortunes / fortunes-fr
and then 
fortune mysoginie -m '' | egrep -v -r "^%" | egrep -v  '\-\+\-' > myso-fr.txt 
fortune tribune-linuxfr  -m '' | egrep -v -r "^%" | egrep -v  '\-\+\-' >  troll.txt

chienne is the text of a feminist site http://www.chiennesdegarde.com/

blague miso is  a random mysoginistic joke on internet. 

The higher a cos is the more two things are similar. 

I used pydot to make a svg map of the path / frequency, just for fun

"""


import os, sys, inspect
cmd_folder = os.path.abspath(
    os.path.join(
        os.path.split(
            inspect.getfile( inspect.currentframe() )
        )[0] ,
        ".."
    )
)
if cmd_folder not in sys.path:
   sys.path.insert(0, cmd_folder)




import re
from vector_dict.VectorDict import VectorDict, tree_from_path, flattening, convert_tree, is_generator
import pydot as pd
from codecs import open as open

def dot_graph( dict_graph, out_name, gopts = dict( rankdir='LR',fontsize = 20.0, size = "10.0,10.0", dpi= 400.0 )):
    graph = pd.Dot(graph_type='digraph', **gopts )
    node = set()
    edge = []
    label = [] 
    for pair in dict_graph.as_row_iter(flatten=False):
        path = [ "ROOT" ] +  list(pair[0]) + list( [ pair[1] ] )  
        ## on vire weigth
        #path.pop(-2) 
        node = node | set( x for x in flattening(path)  )
        
        label += [ u"->".join(unicode(x) for x in path[1::] ) ]

        while len(path) >= 2:
            if isinstance( path[1], int) or ( path[0:2]) not in edge :
                edge += [ ( path[0:2] ) ]
            path.pop(0)
    for n in node:
        graph.add_node( pd.Node( n) )
    for e in edge:
        arg = dict()
        if isinstance(e[1],int):
            arg = dict( label = label.pop(0) )
        graph.add_edge( pd.Edge( e[0], e[1], arrowhead="normal", **arg ))
    graph.write_jpeg(out_name)

t1 = u"""Je vais à la pêche aux moules moules moules, qui viendras avec moi?"""
t2 = u"""je vais à la pêche électorale aux voies"""
t3 = u"""tous les chemins mènent à Rome"""
t4 = u"""Le je du jeu, Jeune je vois, est il une jeunesse ?"""
t5 = u"""je jeune à jeun, jeu à jouer"""


def text_grapher(unicode_text):
    sp_pattern = re.compile( "[\s\-\,\']+", re.M)
    print unicode_text

    res=  VectorDict(int,{} )
    sl =    map( 
                lambda string :  ( convert_tree( { s : { t : 1 }}  ) for s,t in zip( string, string[1:]) ) ,
                map( 
                    lambda string : [ " " ] +    filter(unicode.isalpha,list(string)) + [ " " ] ,
                    map( unicode.lower,sp_pattern.split(unicode_text ) ) 
            )
        )
    for el in sl:
        for i in el:
            res+=i
    res.tprint()
    return res



import random
weighted_choice = lambda s : random.choice(sum(([v]*wt for v,wt in s.iteritems() ) ,[])) 
engl, zara, avenged =  [] , [] , []
all_arr =  []
first = True
for name, arr in [ ("avenged.txt", avenged ),( "english.txt", engl ) ,( "zara.txt", zara) ]:
    transition = text_grapher( open(name,"rt",encoding= "utf-8" ).read() )
    transition.prune( u" " , u" ")
    if first:
        first = False
        dot_graph( transition, 'avenged.jpg' )


    
    for j in range(0,100):
        passw  = " "
        once = 0
        older = 0
        while(len(passw) < 10 ):
            print "%s* %s / %s"% ( passw , once, older)
            passw += weighted_choice( transition[ passw[-1] ]  ) 
            passw = passw.strip()
            if older == len(passw):
                once+=1
            else:
                print "RESET"
                once=0
                older = len(passw)
           
            if once > 3:
                
                once=0
                older= len(passw)
                passw = passw[0:-1] if len(passw) > 2 else " "
                print "**************"
                print passw


           
        arr += [ passw ]


print "english"
print ",".join(engl)


print "zara"
print ",".join(zara)
#
print "avenged"
print ",".join(avenged)


#print "la page de garde de chienne de garde est elle troll ou missogyne? %r ou %r " % (troll.cos( chienne) , zara.cos( chienne))
#blague = text_grapher(  open("blague-myso.txt","rt", encoding='utf-8').read() )
#print "blague mysogyne est elle un troll ou misogyne? %r ou %r " % (troll.cos( blague) , zara.cos( blague))

#print "troll cos mys = %r" % troll.cos( zara )
