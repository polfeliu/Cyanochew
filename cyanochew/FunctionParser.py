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
        return t

    def NAME(self, t):
        return t

    def error(self, value):
        print("Illegal character '%s' at line %s " % (value.value, value.lineno))
        self.index += 1


class Function:pass
class Functiondef:pass
class Comment:pass
class Return:pass
class Sum:pass
class Difference:pass
class Product:pass
class Division:pass
class Power:pass
class Modulus:pass
class BitwiseOr:pass
class BitwiseAnd:pass
class BitshitLeft:pass
class BitshitRight:pass
class ArcTangent:pass
class Declaration:pass
class AssignmentDeclaration:pass
class Assignment:pass
class CmdWrite:pass
class RawRead:pass
class Delay:pass
class Number:pass
class Variable:pass

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

    @_(' { NEWLINE } functiondef "{"  { NEWLINE } statements NEWLINE { NEWLINE } returndef { NEWLINE } "}" { NEWLINE } ')
    def function(self,p):
        f = Function()
        f.functiondef = p.functiondef
        f.statements = p.statements
        f.returndef = p.returndef
        return f

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
        f = Functiondef()
        f.name = p.NAME0
        f.variables = {
            p.NAME1 : p.TYPE0
        }
        for i in range(len(p.NAME2)):
            name = p.NAME2[i]
            type = p.TYPE1[i]
            f.variables[name] = type

        return f

    # Function return variable
    @_('RETURN NAME')
    def returndef(self, p):
        r = Return()
        r.variables = [p.NAME]

    # Function return list of variables
    @_('RETURN "[" NAME { "," NAME } "]"')
    def returndef(self, p):
        r = Return()
        r.variables = [p.NAME0] + p.NAME1

    # Empty declaration
    @_('NAME ":" TYPE')
    def statement(self, p):
        d = Declaration()
        d.variable = p.NAME
        d.type = p.TYPE
        return d

    # Declaration with assignment
    @_('NAME ":" TYPE "=" expr')
    def statement(self, p):
        a = AssignmentDeclaration()
        a.variable = p.NAME
        a.type = p.TYPE
        a.expression = p.expr
        print(p.expr)

    # Reassignment without declaration
    @_('NAME "=" expr')
    def statement(self, p):
        a = Assignment()
        a.variable = p.NAME
        a.expression = p.expr
        return a

    # cmdWrite
    @_(' REGISTER NAME ARROW NAME')
    def statement(self, p):
        c = CmdWrite()
        c.register = p.NAME0
        c.variable = p.NAME1
        return c

    # rawRead
    @_(' NAME ARROW REGISTER NAME')
    def statement(self, p):
        r = RawRead()
        r.register = p.NAME1
        r.variable = p.NAME0
        return r

    # delay
    @_('delaydef "{" { NEWLINE } statements { NEWLINE } "}" ')
    def statement(self, p):
        d = Delay()
        d.delay = p.delaydef
        d.body = p.statements
        return d

    @_('DELAY INT')
    def delaydef(self, p):
        return int(p.INT)

    @_('DELAY FLOAT ')
    def delaydef(self, p):
        return float(p.FLOAT)

    @_('expr "+" expr')
    def expr(self, p):
        d = Difference()
        d.summand0 = p.expr0
        d.summand1 = p.expr1
        return d

    @_('expr "-" expr')
    def expr(self, p):
        d = Difference()
        d.minuend = p.expr0
        d.subtrahend = p.expr1
        return d

    @_('expr "*" expr')
    def expr(self, p):
        p = Product()
        p.factor0 = p.expr0
        p.factor1 = p.expr1
        return p

    @_('expr "/" expr')
    def expr(self, p):
        d = Division()
        d.divident = p.expr0
        d.divisor = p.expr1
        return d

    @_('"-" expr %prec UMINUS')
    def expr(self, p):
        d = Difference()
        n0 =  Number()
        n0.value = 0
        d.minuend = n0
        d.subtrahend = p.expr
        return d

    @_('"(" expr ")"')
    def expr(self, p):
        return p.expr

    @_('INT')
    def expr(self, p):
        n = Number()
        n.value = p.INT
        return n

    @_('FLOAT')
    def expr(self, p):
        n = Number()
        n.value = p.FLOAT
        return n

    @_('NAME')
    def expr(self, p):
        v = Variable()
        v.name = p.NAME
        return v

if __name__ == '__main__':
    lexer = FunctionLexer()
    parser = FunctionParser()
    while True:
        try:
            text = open("script.cyano", 'r').read()
        except EOFError:
            break
        if text:
            #print([tok for tok in lexer.tokenize(text)])
            p = parser.parse(lexer.tokenize(text))
            print(p)

        break