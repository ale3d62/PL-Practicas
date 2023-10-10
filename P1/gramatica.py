from sly import Lexer
from sly import Parser


class CLexer(Lexer):
    
    # Set of token names. This is always required
    tokens = { NUMBER,ID, COMPSIMB,ANDSIMB,ORSIMB}
    # String containing ignored characters
    ignore = ' \t'
    # Regular expression rules for tokens
    literals = { ';', '(', ')','=','<','>','!',"+","-","*","/"}
    ID = r'[a-zA-Z_][a-zA-Z0-9_]*'
    
    COMPSIMB = r'==|<=|>=|!='
    ORSIMB = r'\|\|'
    ANDSIMB =r'\&\&'
    


    ignore_newline = r'\n+'
    @_(r'\d+')

    def NUMBER(self, t):
        t.value = int(t.value)
        return t

    # Line number tracking
    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    def error(self, t):
        print('Line %d: Bad character %r' % (self.lineno, t.value[0]))
        self.index += 1
        


#PARSER
class CParser(Parser):
    Tabla=dict()

    def __init__(self):
        self.vars = {}
    
    tokens = CLexer.tokens
    debugfile='debug.txt'

    # Grammar rules and actions
    @_('OPER ";" S')                     #S = oper ';' S
    def S(self, p):
        return p.OPER #ESTO HAY QUE CAMBIARLO PARA PODER PONER VARIAS INSTRUCCIONES

    @_('')                               #S = epsilon
    def S(self,p):
        pass

    
    @_('ASIG')                       #OPER = ASIG
    def OPER(self,p):
        return p.ASIG

    @_('OROP')                       #OPER = OROP
    def OPER(self,p):
        return p.OROP


    @_('ID "=" OPER')                       #ASIG = ID '=' OPER
    def ASIG(self,p):
        self.Tabla[p.ID]=p.OPER
        return p.OPER


    @_('OROP ORSIMB ANDOP')                 #OROP = OROP '||' ANDOP
    def OROP(self,p):
        return p.OROP or p.ANDOP

    @_('ANDOP')                             #OROP = ANDOP
    def OROP(self,p):
        return p.ANDOP


    @_('ANDOP ANDSIMB NOTOP')               #ANDOP = ANDOP '&&' NOTOP
    def ANDOP(self,p):
        return p.OROP and p.ANDOP

    @_('NOTOP')                             #ANDOP = NOTOP
    def ANDOP(self,p):
        return p.NOTOP


    @_('"!" NOTOP')                       #NOTOP = '!' NOTOP
    def NOTOP(self,p):
        return not p.NOTOP

    @_('COMPOP')                       #NOTOP = '!' NOTOP
    def NOTOP(self,p):
        return p.COMPOP


    @_('COMPOP COMPSIMB ADDOP')                       #NOTOP = COMBOP COMPSIMB ADDOP
    def COMPOP(self,p):
        if(p.COMPSIMB == "=="):
            return p.COMOP == p.ADDOP
        elif(p.COMPSIMB == "<="):
            return p.COMOP <= p.ADDOP
        elif(p.COMPSIMB == ">="):
            return p.COMOP >= p.ADDOP
        elif(p.COMPSIMB == "!="):
            return p.COMOP != p.ADDOP

    @_('ADDOP')
    def COMPOP(self,p):
        return p.ADDOP


    @_('ADDOP "+" PRODOP')
    def ADDOP(self,p):
        return p.ADDOP + p.PRODOP

    @_('ADDOP "-" PRODOP')
    def ADDOP(self,p):
        return p.ADDOP-p.PRODOP

    @_('PRODOP')
    def ADDOP(self,p):
        return p.PRODOP


    @_('PRODOP "*" PAROP')
    def PRODOP(self,p):
        return p.PRODOP * p.PAROP

    @_('PRODOP "/" PAROP')
    def PRODOP(self,p):
        return p.PRODOP / p.PAROP
        
    @_('PAROP')
    def PRODOP(self,p):
        return p.PAROP


    @_('"(" OROP ")"')
    def PAROP(self,p):
        return p.OR


    @_('VAL')
    def PAROP(self,p):
        return p.VAL

    @_('NUMBER')
    def VAL(self,p):
        return p.NUMBER

    @_('ID')
    def VAL(self,p):
        return self.Tabla[p.ID]


    
if __name__ == '__main__':
    lexer = CLexer()
    parser = CParser()
    input = "a = 1 + 1;"
    result = parser.parse(lexer.tokenize(input))
    print(result)

