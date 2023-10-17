from sly import Lexer
from sly import Parser


class CLexer(Lexer):
    
    tokens = {NUMBER,NUMBERF,CHAR, ID, TYPE, COMPSIMB, ANDSIMB, ORSIMB}

    # Ignored characters
    ignore = ' \t'

    literals = { ';', '(', ')', '=', '<', '>', '!', "+", "-", "*", "/", ","}

    # Regular expression rules for tokens
    ID = r'(?!int\b|float\b|char\b)[a-zA-Z_][a-zA-Z0-9_]*'
    
    COMPSIMB = r'==|<=|>=|!='
    ORSIMB = r'\|\|'
    ANDSIMB =r'\&\&'
    TYPE = r'int|float|char'
    NUMBERF=r'[0-9].[0-9]+'
    CHAR=r'\"[a-z]\"'


    ignore_newline = r'\n+'
    @_(r'\d+')

    def NUMBER(self, t):
        t.value = int(t.value)
        return t

    def NUMBERF(self, t):
        t.value = float(t.value)
        return t

    def CHAR(self, t):
        t.value = t.value.replace("\"", "")
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

    def __init__(self):
        self.vars = {}
    
    tokens = CLexer.tokens
    debugfile='debug.txt'


    #GRAMMAR RULES

    @_('S LINE ";"')                        #S = S line ';'
    def S(self, p):
        if(p.S):
            print(p.S)
        return p.LINE

    @_('')                                  #S = epsilon
    def S(self,p):
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



    @_('TYPE IDPRIMA')                           #declar = type idprima
    def DECLAR(self,p):
        list = p.IDPRIMA
        for elem in list:
            self.Table[elem]=[0,p.TYPE]
        return

    @_('IDPRIMA "," ID')                           #idprima = idprima , ID
    def IDPRIMA(self,p):
        list = p.IDPRIMA
        list.append(p.ID)
        return list

    @_('ID')                           #idprima = ID
    def IDPRIMA(self,p):
        return [p.ID]




    @_('TYPE ID "=" INSTR')                 #asig = TYPE ID '=' instr
    def ASIG(self,p):
        try:
            if(p.TYPE=='int'):
                if(type(p.INSTR)==str):
                    self.Table[p.ID]=[ord(p.INSTR),p.TYPE]
                else:
                    self.Table[p.ID]=[int(p.INSTR),p.TYPE]
            elif(p.TYPE=='float'): 
                self.Table[p.ID]=[float(p.INSTR),p.TYPE]
            elif(p.TYPE=='char'): 
                self.Table[p.ID]=[str(p.INSTR),p.TYPE]

            return self.Table[p.ID][0]
        except ValueError:
            raise Exception("Variable '"+p.ID,"' has incompatible type")


    @_('ID "=" INSTR')                 #asig = TYPE ID '=' instr
    def ASIG(self,p):
        try:
            type = self.Table[p.ID][1]
            value = p.INSTR
            if(type=='int'):
                if(type(p.INSTR)==str):
                    value = ord(value)
                else:
                    value = int(value)
            elif(type=='float'): 
                value = float(value)
            elif(type=='char'): 
                value=chr(value)
                
            self.Table[p.ID][0] = value
            return value
        except:
            raise Exception("Variable '"+p.ID+"' undefined")



    ##
    ## OPERACIONES ARITMETICAS
    ##
    @_('OROP ORSIMB ANDOP')                 #orOp = orOp '||' andOp
    def OROP(self,p):
        res = 1 if (p.OROP or p.ANDOP) else 0 #para que devuelva 1 si se hace un or con valores > 1
        return res

    @_('ANDOP')                             #orOp = andOp
    def OROP(self,p):
        return p.ANDOP


    @_('ANDOP ANDSIMB NOTOP')               #andOp = andOp '&&' notOp
    def ANDOP(self,p):
        return (p.ANDOP and p.NOTOP) and 1 #para que devuelva 1 si se hace un and con valores > 1

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
            return self.Table[p.ID][0]
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
        #except Exception as e:
        #    print("[ERROR] " + str(e))

