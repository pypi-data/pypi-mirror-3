from linkgrammar import Parser
p = Parser(verbosity=1)
links = 'a'
ct = 0
beast = 'It is able to handle unknown vocabulary, and make intelligent guesses from context and spelling about the syntactic categories of unknown words.'
while links is not None:
    links = p.parse_sent("This is a test sentence.")
    print ct, len(links)
    ct = ct + 1


