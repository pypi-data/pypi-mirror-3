#!/usr/bin/env python
from linkgrammar import clg, Parser

p = Parser()

class Node(object):
    def __init__(self,type):
        self.type = type
        self.words = []
        
    def __repr__(self):
        if self.words:
            return "<%s: %s>" % (self.type, ', '.join(self.words))
        else:
            return "<%s>" % self.type
    
def get_ctree(ctree):
    label = clg.linkage_constituent_node_get_label(ctree)
    if label in ['NP','VP','S','PP', 'SBAR', 'WHNP','WHPP', 'SINV', 'QP', 'WHADVP', 'PRT', 'ADJP','ADVP']:
        ret = [Node(label)]
    else:
        ret = [label]
    child = clg.linkage_constituent_node_get_child(ctree)
    if child:
        children = get_ctree(child)
        words = [c for c in children if not isinstance(c, Node) and not isinstance(c, list) and len(c) > 0]
        child_nodes = [c for c in children if isinstance(c, Node) or (isinstance(c,list) and len(c) > 0)]
        ret[-1].words = words
        ret.append(child_nodes)
        
    sibling = clg.linkage_constituent_node_get_next(ctree)
    if sibling:
        ret.extend(get_ctree(sibling))
        
    return ret

def con_tree(sent):
    linkages = p.parse_sent(sent)
    ctree = clg.linkage_constituent_tree(linkages[0]._link)
    return get_ctree(ctree)
