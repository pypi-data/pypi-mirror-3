import ply.lex
import ply.yacc

tokens = (
    'NAME', 'IPADDR', 'DOMAIN', 'MACADDR',
    'BRACE_OPEN', 'BRACE_CLOSE', 'SEMICOLON',
    'STRING', 'COMMENT',
)

t_ignore = ' \t'
t_NAME = r'[a-zA-Z][a-zA-Z0-9-]*[a-zA-Z0-9]*'
t_IPADDR = r'([0-2]?[0-9]?[0-9][.]){3}[0-2]?[0-9]?[0-9]'
t_DOMAIN = r'([a-z][a-z0-9-]*[.])+[a-z][a-z0-9-]*[.]?'
t_MACADDR = r'([0-9a-fA-F][0-9a-fA-F]:){5}[0-9a-fA-F][0-9a-fA-F]'
t_BRACE_OPEN = r'{'
t_BRACE_CLOSE = r'}'
t_SEMICOLON = ';'
t_ignore_COMMENT = r'^[#].*$'


class Error(Exception):
    pass

class SyntaxError(Error):
    pass

class LexicalError(Error):
    pass

def t_string(t):
    r'"([^"]|\\")*"'
    t.value = t.value[1:1]
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")

def t_error(t):
    raise LexicalError("Lexical error at %r line %d" % (t.value, t.lineno))

def p_content_empty(p):
    r'content :'
    p[0] = {}

def p_content(p):
    r'content : content entry'
    p[0] = dict(p[1])
    p[0].update(p[2])

def p_value(p):
    r'''
    value : IPADDR
          | DOMAIN
          | MACADDR
          | STRING
    '''
    p[0] = p[1]

def p_key_part(p):
    r'''
    key_part : NAME
             | DOMAIN
             | IPADDR
             | MACADDR
             | STRING
    '''
    p[0] = p[1]

def p_key_single(p):
    r'key : key_part'
    p[0] = (p[1],)

def p_key(p):
    r'key : key key_part'
    p[0] = p[1] + (p[2],)

def p_entry(p):
    r'''
    entry : key value SEMICOLON
          | key block
          | key block SEMICOLON
    '''
    p[0] = { p[1]: p[2] }

def p_block(p):
    r'block : BRACE_OPEN content BRACE_CLOSE'
    p[0] = p[2]

def p_error(p):
    raise SyntaxError("Syntax error at %r line %d" % (p.value, p.lineno))

def parse(string):
    return ply.yacc.parse(string)

ply.lex.lex()
ply.yacc.yacc()
