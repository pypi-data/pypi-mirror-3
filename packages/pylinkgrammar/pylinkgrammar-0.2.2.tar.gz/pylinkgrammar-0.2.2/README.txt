######
README
######

Description
===========
LinkGrammar is a sentence parsing system developed at Carnegie Melon University by John Lafferty, Daniel Sleator, Davy Temperley and others

LinkGrammar is written in C.  This package contains a Pythonic interface to the C library.

Install
=======
You'll need to build and install linkgrammar before running setup.py.

On Ubuntu systems you install the dependencies like so::

    sudo apt-get install liblink-grammar4-dev
    sudo apt-get install cmake
    sudo apt-get install swig
    
Then to install pylinkgrammar::

    pip install pylinkgrammar

How to use
==========
Parsing simple sentences::

    >>> from pylinkgrammar.linkgrammar import Parser
    >>> p = Parser()
    >>> linkages = p.parse_sent("This is a simple sentence.")
    >>> len(linkages)
    2
    >>> print linkages[0].diagram
    
            +-------------------Xp------------------+
            |              +--------Ost-------+     |
            |              |  +-------Ds------+     |
            +---Wd---+-Ss*b+  |     +----A----+     |
            |        |     |  |     |         |     |
        LEFT-WALL this.p is.v a simple.a sentence.n . 

