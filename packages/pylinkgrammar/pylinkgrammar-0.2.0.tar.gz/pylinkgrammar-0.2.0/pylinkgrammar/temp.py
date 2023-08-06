#!/usr/bin/env python
from linkgrammar import clg, Parser

p = Parser()
i = 0
while True:
    i += 1
    print i
    x = p.parse_sent('This is a test sentence.')
    del x
    