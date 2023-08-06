

from code import interact
from prody.atomic.select import FUNCTION_MAP
import pyparsing as  pp 

def foo(sel, loc, tokens, *args):
    print sel
    print ' ' * (loc-1) + '^'
    print tokens
    print args
    #interact(local=locals())

shortlist = pp.alphanums + '''~@#$.:;_','''
longlist = pp.alphanums + '''~!@#$%^&*()-_=+[{}]\|;:,<>./?()' '''

specialchars = pp.Group(pp.Literal('`') + 
                        pp.Optional(pp.Word(longlist + '"')) + 
                        pp.Literal('`'))
def specialCharsParseAction(token):
    if len(token[0]) == 2: # meaning `` was used
        return '_'
    else:
        return token[0][1]
specialchars.setParseAction(specialCharsParseAction)
regularexp = pp.Group(pp.Literal('"') + 
                      pp.Optional(pp.Word(longlist + '`')) + 
                      pp.Literal('"'))
def regularExpParseAction(sel, loc, token): 
    token = token[0]
    if len(token) == 2:
        return RE.compile('^()$')
    else:
        try:
            regexp = RE.compile(token[1])
        except:
            raise SelectionError(sel, loc, 'failed to compile regular '
                            'expression {0:s}'.format(repr(token[1])))
        else:
            return regexp
regularexp.setParseAction(regularExpParseAction)
oneormore = pp.OneOrMore(pp.Word(shortlist) | regularexp | 
                         specialchars)
funcnames = FUNCTION_MAP.keys()
functions = pp.Keyword(funcnames[0])
for func in funcnames[1:]:
    functions = functions | pp.Keyword(func)

parser = pp.operatorPrecedence(
     oneormore,
     [#(functions, 1, pp.opAssoc.RIGHT, foo),
      (pp.oneOf('+ -'), 1, pp.opAssoc.RIGHT, foo),
      (pp.oneOf('** ^'), 2, pp.opAssoc.LEFT, foo),
      (pp.oneOf('* / %'), 2, pp.opAssoc.LEFT, foo),
      (pp.oneOf('+ -'), 2, pp.opAssoc.LEFT, foo),
      (pp.oneOf('< > <= >= == = !='), 2, pp.opAssoc.LEFT, foo),
      #(pp.Keyword('not') |
      # pp.Regex('(ex)?bonded to') |
      # pp.Regex('(ex)?bonded [0-9]+ to') |
      # pp.Regex('same [a-z]+ as') | 
      # pp.Regex('(ex)?within [0-9]+\.?[0-9]* of'), 
      #          1, pp.opAssoc.RIGHT, foo),
      (pp.Keyword('&&&'), 2, pp.opAssoc.LEFT, foo),
      (pp.Keyword('or'), 2, pp.opAssoc.LEFT, foo),]
    )
    
parser.setParseAction(lambda *args: foo(*(args + ('parseaction',))))
parser.leaveWhitespace()
parse = lambda string: parser.parseString(string, parseAll=True).asList()
