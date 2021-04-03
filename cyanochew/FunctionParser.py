import ply.lex as lex
import ply.yacc as yacc
import sys
import warnings
warnings.simplefilter('always', UserWarning)

class FunctionLexer(object):
    # List of token names.   This is always required
    tokens = (
        'INT',
        'FLOAT',
        'NAME',
        'PLUS',
        'MINUS',
        'DIVIDE',
        'MULTIPLY',
        'EQUALS'
    )

    # Regular expression rules for simple tokens
    t_PLUS = r'\+'
    t_MINUS = r'\-'
    t_MULTIPLY = r'\*'
    t_DIVIDE = r'\/'
    t_EQUALS = r'\='

    def t_FLOAT(self,t):
        r'\d+\.\d+'
        t.value = float(t.value)
        return t

    def t_INT(self,t):
        r'\d+'
        t.value = int(t.value)
        return t

    def t_NAME(self,t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        t.type = 'NAME'
        return t

    # A string containing ignored characters (spaces and tabs)
    t_ignore = ' \t'

    # Error handling rule
    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    # Build the lexer
    def build(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)

    def __init__(self):
        self.build()

    # Test it output
    def test(self, data):
        self.lexer.input(data)
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            print(tok)

class FunctionParser():

    tokens = FunctionLexer.tokens

    precedence = (
        ('left', 'PLUS', 'MINUS'),
        ('left', 'MULTIPLY', 'DIVIDE')
    )

    def p_calc(self, p):
        '''
        calc : expression
             | var_assign
             | empty
        '''
        print(self.run(p[1]))

    def p_var_assign(self, p):
        '''
        var_assign : NAME EQUALS expression
        '''
        p[0] = ('=', p[1], p[3])

    def p_expression(self, p):
        '''
        expression : expression MULTIPLY expression
        | expression DIVIDE expression
        | expression PLUS expression
        | expression MINUS expression
        '''
        p[0] = (p[2], p[1], p[3])

    def p_expression_int_float(self, p):
        '''
        expression : INT
                    | FLOAT
        '''
        p[0] = p[1]

    def p_expression_var(self, p):
        '''
        expression : NAME
        '''
        p[0] = ('var', p[1])

    def p_empty(self, p):
        '''
        empty :
        '''
        p[0] = None

    def p_error(self, p):
        print("Parsing error")

    env = {}
    def run(self, p):
        if type(p) == tuple:
            if len(p) >= 1:
                if p[1] is None:
                    return None
            elif len(p) >= 2:
                if p[2] is None:
                    return None

            if p[0] == '+':
                return self.run(p[1]) + self.run(p[2])
            elif p[0] == '-':
                return self.run(p[1]) - self.run(p[2])
            elif p[0] == '*':
                return self.run(p[1]) * self.run(p[2])
            elif p[0] == '/':
                return self.run(p[1]) / self.run(p[2])
            elif p[0] == '=':
                self.env[p[1]] = self.run(p[2])
            elif p[0] == 'var':
                if p[1] not in self.env:
                    warnings.warn('Undeclared Variable')
                    return None
                else:
                    return self.env[p[1]]
        else:
            return p

    def __init__(self):
        print("building")
        self.lexer = FunctionLexer()
        self.parser = yacc.yacc(module=self)

    def parse(self, p):
        self.parser.parse(p)

p = FunctionParser()

while True:
    try:
        s = input('>>')
    except EOFError:
        break
    p.parse(s)