#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys 
import subprocess
from subprocess import call
import argparse
import os
import time

__author__ = 'Pulkit Kathuria'
__contact__ = 'http://www.jaist.ac.jp/~s1010205/html/ContactMe.html'
__pyfile__ = 'http://www.jaist.ac.jp/~s1010205/bib_tex2item/bib_tex2items.py'
__documentation__ = 'http://www.jaist.ac.jp/~s1010205/bib_tex2item/html/index.html'


class Tex2Items(object):
    def __init__(self, refs):
        """
        @refs: file name @type <str>
        """
        self.refs = refs
    def callLatex(self, command):
        #Call unix commands
        process = subprocess.Popen(command, stdout=subprocess.PIPE)
        output = process.communicate()[0]
        return
    def refsTex(self, refs):
        """
        @tex: write file contents for refs.tex
        """
        tex = """
        \\documentclass{article}
        \\begin{document}
        \\nocite{*}
        \\bibliography{%s}
        \\bibliographystyle{plain}
        \\end{document}"""%self.refs
        with open(refs+'.tex','wb') as f_refs: f_refs.write(tex)
        return refs
    def callCommands(self):
        #build bbl, aux, log
        #Pre-requisite: Latex, bibtex
        commands = [('latex', self.refs),
                    ('bibtex', self.refs),
                    ('bibtex', self.refs),
                    ('latex', self.refs)]
        for command in commands: self.callLatex(command)
    def clean(self):
        #Clean following extensions
        removals = [self.refs+'.dvi', self.refs+'.log',
                    self.refs+'.blg', self.refs+'.aux',
                    self.refs+'.tex']
        for f_name in removals:
            try: os.remove(f_name)
            except: pass
def tex2items(refs):
    """
    input is *.bib file text by readlines(), out is written to a file with extension *.bbl
    """
    message = "Bib items written to %s.bbl"%(refs.strip('.bib'))
    print "%s Found. Opened %s.bbl for writing"%(refs, refs.strip('.bib'))
    print '***************************************'
    for i in range(101):
        sys.stdout.write('%3d%%\r' % i)
        sys.stdout.flush()
        time.sleep(.009)
    refs = refs.strip('.bib')
    bibOperation = Tex2Items(refs)
    bibOperation.refsTex(refs)
    bibOperation.callCommands()
    bibOperation.clean()
    print message
    return 
if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help = True)
    parser = argparse.ArgumentParser(description= 'Usage: python bib2bbl.py -b yourBibfile.bib')
    parser.add_argument('-b','--bib', action="store", nargs = 1, dest="file", type=argparse.FileType('rt'), help='-b bibliography.bib')
    myarguments = parser.parse_args()
    if not myarguments.file:
        parser.print_help()
        exit
    else:
        bib = myarguments.file[0].readlines()
        refs = myarguments.file[0].name
        tex2items(refs)

    
