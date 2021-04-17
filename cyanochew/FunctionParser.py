from sly import Lexer, Parser

class FunctionLexer(Lexer):
    tokens = {
        'TYPE', 'FUN', 'RETURN', 'REGISTER', 'DELAY', 'ARROW', 'NAME', 'INT', 'FLOAT', 'NEWLINE'
        }
    ignore = ' '
    literals = { '=', '+', '-', '*', '/', '(', ')', ':', ",", "#", "[", "]", "{", "}"}

    # Tokens
    TYPE = r'int8|int16|int32|uint8|uint16|uint32|float32|float64'
    FUN = 'fun'
    RETURN = 'return '
    REGISTER = r'register '
    DELAY = r'delay for'
    ARROW = r'<-'
    NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'
    NEWLINE = '\n'

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

    def TYPE(self, t):
        t.value = t.value
        return t

    def NAME(self, t):
        t.value = t.value.upper()
        return t

    def error(self, value):
        print("Illegal character '%s' at line %s " % (value.value, value.lineno))
        self.index += 1

class FunctionParser(Parser):
    tokens = FunctionLexer.tokens

    debugfile = 'parser.out'

    precedence = (
        ('left', '+', '-'),
        ('left', '*', '/'),
        ('right', 'UMINUS'),
        )

    def __init__(self):
        self.names = { }

    @_(' { NEWLINE } { function } { NEWLINE } ')
    def program(self, p):
        pass

    @_('functiondef "{"  { NEWLINE } statements NEWLINE { NEWLINE } returndef { NEWLINE } "}" ')
    def function(self,p):
        pass

    # Statement
    @_('statements NEWLINE { NEWLINE } statement')
    def statements(self, p):
        p.statements.append(p.statement)
        return p.statements
    
    @_('statement')
    def statements(self, p):
        return [p.statement]


    # Function declaration
    @_('FUN NAME "(" NAME  ":" TYPE { "," NAME  ":" TYPE } ")" ')
    def functiondef(self, p):
        print(p.NAME1, p.TYPE0, p.NAME2, p.TYPE1)

    # Function return variable
    @_('RETURN NAME')
    def returndef(self, p):
        print(p)

    # Function return list of variables
    @_('RETURN "[" NAME { "," NAME } "]"')
    def statement(self, p):
        print(p.NAME0, p.NAME1)

    # Empty declaration
    @_('NAME ":" TYPE')
    def statement(self, p):
        print(p)

    # Declaration with assignment
    @_('NAME ":" TYPE "=" expr')
    def statement(self, p):
        print(p.expr)

    # Reassignment without declaration
    @_('NAME "=" expr')
    def statement(self, p):
        self.names[p.NAME] = p.expr

    # cmdWrite
    @_(' REGISTER NAME ARROW NAME')
    def statement(self, p):
        print("cmdWrite")

    # rawRead
    @_(' NAME ARROW REGISTER NAME')
    def statement(self, p):
        print("cmdRead")

    # delay
    @_('delaydef "{" { NEWLINE } statements { NEWLINE } "}" ')
    def statement(self, p):
        print("qwer")

    @_('DELAY INT')
    def delaydef(self, p):
        print("delay")

    @_('DELAY FLOAT ')
    def delaydef(self, p):
        print("delay")

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
            text = open("script.cyano", 'r').read()
        except EOFError:
            break
        if text:
            print([tok for tok in lexer.tokenize(text)])
            #p = parser.parse(lexer.tokenize(text))
            print(parser.log)

        break