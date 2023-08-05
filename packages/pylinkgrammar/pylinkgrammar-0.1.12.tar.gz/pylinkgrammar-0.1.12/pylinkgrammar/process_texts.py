from string import split
import sys,os
import fnmatch
from linkgrammar import Parser, clg
from meta import segment
from meta.tokenizer import TreebankTokenizer

def get_all_files(file_path):
    if file_path[-1] != "/":
        file_path += "/"
    out_files = []
    for root, dirs, files in os.walk(file_path):
        out_files.extend([os.path.join(root, f).replace(file_path + "/", '') for f in files if fnmatch.fnmatch(f,'*.txt')])
    return out_files
    
def get_sentences(text):
    """
    Use the meta.segment's simple regex system for splitting sentences.
    Give a piece of text, return a list of sentences, stripped of outer whitespace.
    """
    return segment.regexSentenceToLines(text).split('\n')

files = get_all_files(sys.argv[1])
sent_count = 0
successes = 0
p = Parser()
for fn in files:
    f = open(fn)
    #Remove page break characters and convert to linux-style line endings if windows ones exist.
    t = f.read().replace('\x0c','').replace('\r','')
    sents = get_sentences(t)
    link_trees = []
    for s in sents:
        sent_count+= 1
        linkages = p.parse_sent(s)
        if linkages:
            successes += 1
            link_trees.append("%s\n%s" % (s, linkages[0].print_diagram()))
        if not linkages:
            link_trees.append("Could not parse: %s" % s)
            print s
        del linkages
    f2 = open('/'.join(split(fn,'/')[:-1]) + "/linkages_" + split(fn,'/')[-1],'w')
    f2.write('\n\n'.join(link_trees))
    f2.close()
print successes, sent_count, float(successes)/sent_count