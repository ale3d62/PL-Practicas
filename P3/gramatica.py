from sly import Lexer
from sly import Parser


class CLexer(Lexer):
    
    tokens = {NUMBER,NUMBERF,CHAR, ID, TYPE, COMPSIMB, ANDSIMB, ORSIMB}

    # Ignored characters
    ignore = ' \t'

    literals = { ';', '(', ')', '=', '<', '>', '!', "+", "-", "*", "/", ",",'{','}'}

    # Regular expression rules for tokens
    ID = r'(?!int\b|float\b|char\b)[a-zA-Z_][a-zA-Z0-9_]*'
    
    COMPSIMB = r'==|<=|>=|!='
    ORSIMB = r'\|\|'
    ANDSIMB =r'\&\&'
    TYPE = r'int|float|char'


    ignore_newline = r'\n+'

    @_(r'\d+')
    def NUMBER(self, t):
        t.value = int(t.value)
        return t

    @_(r'\d.\d+')
    def NUMBERF(self, t):
        t.value = float(t.value)
        return t

    @_(r'\"[a-z]\"|\'[a-z]\'')
    def CHAR(self, t):
        t.value = t.value.replace("\"", "")
        t.value = t.value.replace("\'", "")
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
    Table=dict()
    ambito="None"

    def __init__(self):
        self.vars = {}
    
    tokens = CLexer.tokens
    debugfile='debug.txt'


    #GRAMMAR RULES
    @_('S FUNCTION')
    def S(self,p):
        pass
    @_('')
    def S(self,p):
        pass
    @_('TYPE ID emptyF1 "(" ARGS ")" "{" LINES "}"')
    def FUNCTION(self,p):
        pass
    @_('TYPE ARG RARGS' )
    def ARGS(self,p):
        pass

    @_('')
    def ARGS(self,p):
        pass

    @_('"," TYPE ARG RARGS')
    def RARGS(self,p):
        pass
    @_('')
    def emptyF1(self,p):
        self.ambito=p[-1]
        self.Table[self.ambito]=[p[-2],dict()]
        return p[-2]
    @_('')
    def RARGS(self,p):
        pass
    @_('ID')
    def ARG(self,p):
        self.Table[self.ambito][1][p.ID]=[0,p[-2]]
        return 
    @_('LINES LINE ";"')                        #S = S line ';'
    def LINES(self, p):
        return p.LINE

    @_('')                                  #S = epsilon
    def LINES(self,p):
        pass


    ##
    ## ENTRADA PRINCIPAL
    ##
    @_('INSTR')                        #LINE = instr
    def LINE(self, p):
        return p.INSTR

    @_('DECLAR')                        #LINE = declar
    def LINE(self, p):
        return p.DECLAR


    ##
    ## INSTRUCCIONES DEL LENGUAJE
    ##
    @_('ASIG')                              #instr = asig
    def INSTR(self,p):
        return p.ASIG

    @_('OROP')                              #instr = orOp
    def INSTR(self,p):
        return p.OROP

    #DECLARACIONES
    @_('TYPE IDPRIMA')
    def DECLAR(self,p):
        pass

    @_('empty ELEM REST')
    def IDPRIMA(self,p):
        pass
        
    @_('"," empty2 ELEM REST')
    def REST(self,p):
        pass

    @_('')
    def REST(self,p):
        pass

    @_('ID')
    def ELEM(self,p):
        self.Table[self.ambito][1][p.ID] =[0, p[-2]]

    @_('ID "=" INSTR')
    def ELEM(self,p):
        valueType = p[-4]
        value = p.INSTR
        if(valueType=='int'):
            if(type(value)==str):
                value = ord(value)
            else:
                value = int(value)
        elif(valueType=='float'): 
            value = float(value)
        elif(valueType=='char'): 
            value=chr(value)
            
        self.Table[self.ambito][1][p.ID]= [value, valueType]

    #SIMULACION DE HERENCIA
    @_('')
    def empty(self, p):
        return p[-1]

    @_('')
    def empty2(self, p):
        return p[-3]




    @_('ID "=" INSTR')                 #asig = ID '=' instr
    def ASIG(self,p):
        try:
            type = self.Table[self.ambito][1][p.ID][1]
            value = p.INSTR
            if(type=='int'):
                if(type(value)==str):
                    value = ord(value)
                else:
                    value = int(value)
            elif(type=='float'): 
                value = float(value)
            elif(type=='char'): 
                value=chr(value)
                
            self.Table[self.ambito][1][p.ID][0] = value
            return self.Table[self.ambito][1][p.ID][0]
        except:
            raise Exception("Variable '"+p.ID+"' undefined")



    ##
    ## OPERACIONES ARITMETICAS
    ##
    @_('OROP ORSIMB ANDOP')                 #orOp = orOp '||' andOp
    def OROP(self,p):
        res = 1 if (p.OROP or p.ANDOP) else 0 #in order to return 1 if or is done with values > 1
        return res

    @_('ANDOP')                             #orOp = andOp
    def OROP(self,p):
        return p.ANDOP


    @_('ANDOP ANDSIMB NOTOP')               #andOp = andOp '&&' notOp
    def ANDOP(self,p):
        return (p.ANDOP and p.NOTOP) and 1 #in order to return 1 if and is done with values > 1

    @_('NOTOP')                             #andOp = notOp
    def ANDOP(self,p):
        return p.NOTOP


    @_('"!" NOTOP')                         #notOp = '!' notOp
    def NOTOP(self,p):
        return not p.NOTOP

    @_('COMPOP')                            #notOp = compOp
    def NOTOP(self,p):
        return p.COMPOP


    @_('COMPOP COMPSIMB ADDOP')             #compOp = compOp compSimb addOp
    def COMPOP(self,p):
        if(p.COMPSIMB == "=="):
            return p.COMPOP == p.ADDOP
        elif(p.COMPSIMB == "<="):
            return p.COMPOP <= p.ADDOP
        elif(p.COMPSIMB == ">="):
            return p.COMPOP >= p.ADDOP
        elif(p.COMPSIMB == "!="):
            return p.COMPOP != p.ADDOP

    @_('ADDOP')                             #compOp = addOp
    def COMPOP(self,p):
        return p.ADDOP


    @_('ADDOP "+" PRODOP')                  #addOp = addOp + prodOp
    def ADDOP(self,p):
        return p.ADDOP + p.PRODOP

    @_('ADDOP "-" PRODOP')                  #addOp = addOp - prodOp
    def ADDOP(self,p):
        return p.ADDOP-p.PRODOP

    @_('PRODOP')                            #addOp = prodOp
    def ADDOP(self,p):
        return p.PRODOP


    @_('PRODOP "*" PAROP')                  #prodOp = prodOp * parOp
    def PRODOP(self,p):
        return p.PRODOP * p.PAROP

    @_('PRODOP "/" PAROP')                  #prodOp = prodOp / parOp
    def PRODOP(self,p):
        return p.PRODOP / p.PAROP
    ##
    ## PARENTESIS
    ## 
    @_('PAROP')                             #prodOp = parOp
    def PRODOP(self,p):
        return p.PAROP


    @_('"(" OROP ")"')                      #parOp = (orOp)
    def PAROP(self,p):
        return p.OROP

    ##
    ## SIMBOLOS TERMINALES
    ##
    @_('VAL')                               #parOp = val
    def PAROP(self,p):
        return p.VAL

    @_('NUMBER')                            #val = NUMBER
    def VAL(self,p):
        return p.NUMBER

    @_('NUMBERF')                            #val = NUMBERF
    def VAL(self,p):
        return p.NUMBERF

    @_('CHAR')                            #val = CHAR
    def VAL(self,p):
        return p.CHAR

    @_('ID')                                #val = ID
    def VAL(self,p):
        try:
            return self.Table[self.ambito][1][p.ID][0]
        except:
            raise Exception("Variable '"+p.ID+"' undefined") 


    
if __name__ == '__main__':
    lexer = CLexer()
    parser = CParser()
    text = ""
    while(text != "exit"):
        #try:
        text = input("Enter instructions separated by ';' [or writte 'exit' to exit]\n")
        result = parser.parse(lexer.tokenize(text))
        print(result)
        print(parser.Table)
        #except Exception as e:
        #    print("[ERROR] " + str(e))

