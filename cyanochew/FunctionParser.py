from sly import Lexer, Parser

class FunctionLexer(Lexer):
    tokens = {
        'NAME', 'INT', 'FLOAT'
        }
    ignore = ' \t'
    literals = { '=', '+', '-', '*', '/', '(', ')'}

    # Tokens
    NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'

    @_(r"\d+\.\d*")
    def FLOAT(self, t):
        t.value = float(t.value)
        return t

    @_(r'\d+')
    def INT(self, t):
        t.value = int(t.value)
        return t

    @_(r'\n+')
    def newline(self, t):
        self.lineno += t.value.count('\n')

    def NAME(self, t):
        t.value = t.value.upper()
        return t

    def error(self, value):
        print("Illegal character '%s' at line %s " % (value.value, value.lineno))
        self.index += 1

class FunctionParser(Parser):
    tokens = FunctionLexer.tokens

    precedence = (
        ('left', '+', '-'),
        ('left', '*', '/'),
        ('right', 'UMINUS'),
        )

    def __init__(self):
        self.names = { }

    @_('NAME "=" expr')
    def statement(self, p):
        self.names[p.NAME] = p.expr

    @_('expr')
    def statement(self, p):
        print(p.expr)

    @_('expr "+" expr')
    def expr(self, p):
        return p.expr0 + p.expr1

    @_('expr "-" expr')
    def expr(self, p):
        return p.expr0 - p.expr1

    @_('expr "*" expr')
    def expr(self, p):
        return p.expr0 * p.expr1

    @_('expr "/" expr')
    def expr(self, p):
        return p.expr0 / p.expr1

    @_('"-" expr %prec UMINUS')
    def expr(self, p):
        return -p.expr

    @_('"(" expr ")"')
    def expr(self, p):
        return p.expr

    @_('INT')
    def expr(self, p):
        return p.INT

    @_('FLOAT')
    def expr(self, p):
        return p.FLOAT

    @_('NAME')
    def expr(self, p):
        try:
            return self.names[p.NAME]
        except LookupError:
            print("Undefined name '%s'" % p.NAME)
            return 0

if __name__ == '__main__':
    lexer = FunctionLexer()
    parser = FunctionParser()
    while True:
        try:
            text = input('calc > ')
        except EOFError:
            break
        if text:
            parser.parse(lexer.tokenize(text))