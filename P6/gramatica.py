from sly import Lexer
from sly import Parser


class BinaryNode():
    def __init__(self, op, p1, p2):
        if(op=='and'):
            self.value = p1 and p2
        elif(op=='or'):
            #in order to return 1 if or is done with values > 1
            if (p1 or p2): self.value = 1 
            else: self.value = 0
        elif(op=='=='):
            self.value = p1 == p2
        elif(op=='<='):
            self.value = p1 <= p2
        elif(op=='>='):
            self.value = p1 >= p2
        elif(op=='!='):
            self.value = p1 != p2
        elif(op=='+'):
           print("movl %eax, %ebx;\npopl %eax;\naddl %ebx,%eax;\npushl %eax\n")
           self.value=p1+p2
        elif(op=='-'):
            print("movl %eax, %ebx;\npopl %eax;\nsubl %ebx,%eax;\npushl %eax\n")
            self.value=p1-p2
        elif(op=='*'):
             print("\nmovl %eax, %ebx;\npopl %eax;\nimmull %ebx,%eax;\npushl %eax\n")
             self.value=p1*p2
        elif(op=='/'):
             self.value=p1/p2
             print("\nmovl %eax, %ebx;\npopl %eax;\ncdq;\nsubl idivl %ebx;\npushl %eax\n")
        elif(op=='asig'):
            p1.value = p2


class UnaryNode():
    def __init__(self, op, p1):
        if(op=='not'):
            self.value = not p1







class CLexer(Lexer):
    
    tokens = {NUMBER,NUMBERF,CHAR, ID, TYPE,VOIDTYPE, COMPSIMB, ANDSIMB, ORSIMB,MAIN,PRINT,SCANF, STRING}

    # Ignored characters
    ignore = ' \t'

    literals = { ';', '(', ')', '=', '<', '>', '!', "+", "-", "*", "/", ',','{','}', '&', '[', ']'}

    # Regular expression rules for tokens
    ID = r'(?!int\b|float\b|char\b|void\b|main\b|printf\b|scanf\b|\[|\])[a-zA-Z_][a-zA-Z0-9_]*'
    
    COMPSIMB = r'==|<=|>=|!='
    ORSIMB = r'\|\|'
    ANDSIMB =r'\&\&'
    TYPE = r'int|float|char'
    VOIDTYPE = r'void'
    
    MAIN = r'main'
    PRINT= r'printf'
    SCANF=r'scanf'


    ignore_newline = r'\n+'

    @_(r'\d+')
    def NUMBER(self, t):
        t.value = int(t.value)
        return t

    @_(r'\d.\d+')
    def NUMBERF(self, t):
        t.value = float(t.value)
        return t

    @_(r'\'[a-z]\'')
    def CHAR(self, t):
        t.value = t.value.replace("\'", "")
        return t
        
    @_(r'\".*\"')
    def STRING(self,t):
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
    ambito="Global"
    ebpOffset = 0
    ebpOffsetArg = 0

    def __init__(self):
        self.vars = {}
    
    tokens = CLexer.tokens
    debugfile='debug.txt'


    #-------------------------------------------------
    #-------------GRAMMAR RULES-----------------------
    #-------------------------------------------------

    ##
    ## FUNCTIONS
    ##
    @_('S2 TYPE emptymain MAIN "(" ")" "{" LINES "}"')
    def S(self,p):
        pass

    @_("")
    def emptymain(self,p):
        self.ambito="main"
        self.Table[self.ambito]=["int",dict()]
        pass
        
    @_('S2 FUNCTION')
    def S2(self,p):
        pass
    
    @_('')
    def S2(self,p):
        pass
    
    

    @_('TYPE ID emptyF1 "(" ARGS ")" "{" LINES "}" emptyF2')
    def FUNCTION(self,p):
        pass

    @_('VOIDTYPE ID emptyF1 "(" ARGS ")" "{" LINES "}" emptyF2')
    def FUNCTION(self,p):
        pass

    #Esto lo pilla la gramatica sin explotar, pero en realidad detras de ID faltaria "POINTERS empty ", la semantica de añadir a la tabla y todo eso casi que no se puede hacer sin el empty, solo pilla el tipo bien el primer elemento
    @_('TYPE ID ARRAY REST ";"') #Global declarations
    def FUNCTION(self,p):
        arraySizes = p.ARRAY
        if (len(arraySizes) > 0):
            #el array se inicializa a [0] y al tipo se le añade un [],
            #pongo esto por poner algo, ya que luego no se va a usar
            #El ebpoffset esta a 0 porque algo hay que poner, pero no es asi
            self.Table[self.ambito][1][p.ID] =[[0], p[-4]+p[-3]+"[]", 0]
        else:
            print(p.ID + ": " + str(p[-5]))
            self.Table[self.ambito][1][p.ID] =[0, p[-5], self.ebpOffset]

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
        self.ebpOffsetArg += 4
        self.ambito=p[-1]
        self.Table[self.ambito]=[p[-2],dict(), self.ebpOffsetArg]
        return p[-2]
    @_('')
    def emptyF2(self,p):
        self.ebpOffsetArg += 4
        self.ambito="Global"
        pass

    @_('')
    def RARGS(self,p):
        pass

    @_('ID')
    def ARG(self,p):
        self.Table[self.ambito][1][p.ID]=[0,p[-2], self.ebpOffsetArg]
        return 

    

    @_('LINES LINE ";"')                        #S = S line ';'
    def LINES(self, p):
        return p.LINE

    @_('')                                  #S = epsilon
    def LINES(self,p):
        pass


    ##
    ## MAIN INPUT
    ##
    @_('INSTR')                        #LINE = instr
    def LINE(self, p):
        return p.INSTR

    @_('DECLAR')                        #LINE = declar
    def LINE(self, p):
        return p.DECLAR
        
    @_('SCANF "(" STRING SCANIDS ")"')
    def LINE(self,p):
        L=list()
        L=p.SCANIDS
        percents=p.STRING.count("%d")
        vars=len(L)
        print("pushl "+p.STRING)
        print("Call scanf;")
        print("addl $"+str((vars+1)*4)+",%esp;")
        if vars==percents:
           pass
        else:
            raise Exception("Too many variables in scanf")
                
            
    @_(", REFERENCE SCANIDS ")
    def SCANIDS(self,p):
        L=[]
        L.append(p.REFERENCE)
        
        L += p.SCANIDS
        return L
    @_("")
    def SCANIDS(self,p):
        return []
    @_('PRINT "(" STRING PRINTIDS ")"')
    def LINE(self, p):
        L=list()
        L=p.PRINTIDS
        percents=p.STRING.count("%d")
        if(L):
            vars=len(L)
        else:
            vars = 0
            L = []
        if(vars!=percents): 
            raise Exception("Too many variables in printf")
        else:
            s=p.STRING
            for var in L:
                s = s.replace("%d",str(var),1)
            print("pushl "+p.STRING)
            print("Call printf")
            print("addl $"+str((vars+1)*4)+",%esp")
    
    
    @_('"," INSTR PRINTIDS')
    def PRINTIDS(self,p):
        L=[]
        L.append(p.INSTR)
        
        L += p.PRINTIDS
        return L
        
    @_('')
    def PRINTIDS(self,p):
        return []

    ##
    ## LANGUAJE INSTRUCTIONS
    ##
   # @_('ID "("    )')
    @_('ASIG')                              #instr = asig
    def INSTR(self,p):
        return p.ASIG

    @_('OROP')                              #instr = orOp
    def INSTR(self,p):
        return p.OROP
    @_('FCALL')
    def INSTR(self,p):
        pass
    @_('ID "(" FARGS ")"')
    def FCALL(self,p):
        L=(p.FARGS)
        if(len(L)==len(self.Table[p.ID][1])):
            print("Call "+p.ID+"\n")
            print("addl $"+str(len(L)*4)+",%esp")
        
        pass
    @_('FARG RFARGS' )
    def FARGS(self,p):
        L=[]
        L.append(p.FARG)      
        L += p.RFARGS
        return L
    
    @_('')
    def FARGS(self,p):
        pass

    @_('"," FARG RFARGS')
    def RFARGS(self,p):
        L=[]
        L.append(p.FARG)
        
        L += p.RFARGS
        return L
        
    @_('')
    def RFARGS(self,p):
        return []
    @_('VAL')
    def FARG(self,p):
        return p.VAL  
    #DECLARATIONS
    @_('TYPE POINTERS IDPRIMA')
    def DECLAR(self,p):
        print("subl $"+str(-1*self.ebpOffset)+", %esp")
        pass

    @_('"*" POINTERS')
    def POINTERS(self,p):
        return p.POINTERS + "*"

    @_('')
    def POINTERS(self,p):
        return ''

    @_('empty ELEM REST')
    def IDPRIMA(self,p):
        pass
        
    @_('"," empty2 ELEM REST')
    def REST(self,p):
        pass

    @_('')
    def REST(self,p):
        pass

        
    #Esto hay que cambiarlo para que meta los tipos puntero
    @_('ID ARRAY')
    def ELEM(self,p):
        arraySizes = p.ARRAY
        if (len(arraySizes) > 0):
            #el array se inicializa a [0] y al tipo se le añade un [],
            #pongo esto por poner algo, ya que luego no se va a usar
            #El ebpoffset esta a 0 porque algo hay que poner, pero no es asi
            self.Table[self.ambito][1][p.ID] =[[0], p[-4]+p[-3]+"[]", 0]
        else:
            self.Table[self.ambito][1][p.ID] =[0, p[-3], self.ebpOffset]

    @_('"[" NUMBER "]" ARRAY')
    def ARRAY(self,p):
        arraySizes = p.ARRAY
        arraySizes.append(p.NUMBER)
        return arraySizes

    @_('')
    def ARRAY(self,p):
        return []


    @_('ID "=" INSTR')
    def ELEM(self,p):
        #valueType = p[-6]+p[-4] #no se que hacia esto asi pero p[-6] devuelve nonetype y p[-4] el tipo
        valueType = p[-4]
        value = p.INSTR
        if(valueType=='int'):
            # if(type(value)==str):
            #     value = ord(value)
            # else:
            value = int(value)
        elif(valueType=='float'): 
            value = float(value)
        elif(valueType=='char'): 
            value=chr(value)
            
        self.Table[self.ambito][1][p.ID]= [value, valueType, self.ebpOffset]

    #INHERITANCE SIMULATION
    @_('')
    def empty(self, p):
        self.ebpOffset-=4
        
        return p[-2]

    @_('')
    def empty2(self, p):
        self.ebpOffset-=4
        return p[-3]




    @_('ID "=" INSTR')                 #asig = ID '=' instr
    def ASIG(self,p):
        try:
            type = self.Table[self.ambito][1][p.ID][1]
            value = p.INSTR
            if(type=='int'):
                #if(type(value)==str):
                #    value = ord(value)
                #else:
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
    ## ARITMETICAL OPERATIONS
    ##
    @_('OROP ORSIMB ANDOP')                 #orOp = orOp '||' andOp
    def OROP(self,p):
        #res = 1 if (p.OROP or p.ANDOP) else 0 #in order to return 1 if or is done with values > 1
        return BinaryNode("or",p.OROP,p.ANDOP).value
        

    @_('ANDOP')                             #orOp = andOp
    def OROP(self,p):
        return p.ANDOP


    @_('ANDOP ANDSIMB NOTOP')               #andOp = andOp '&&' notOp
    def ANDOP(self,p):
        return BinaryNode("and", p.ANDOP, p.NOTOP).value
        #return (p.ANDOP and p.NOTOP) and 1 #in order to return 1 if and is done with values > 1

    @_('NOTOP')                             #andOp = notOp
    def ANDOP(self,p):
        return p.NOTOP


    @_('"!" NOTOP')                         #notOp = '!' notOp
    def NOTOP(self,p):
        return UnaryNode("not", p.NOTOP).value
        #return not p.NOTOP

    @_('COMPOP')                            #notOp = compOp
    def NOTOP(self,p):
        return p.COMPOP


    @_('COMPOP COMPSIMB ADDOP')             #compOp = compOp compSimb addOp
    def COMPOP(self,p):
        if(p.COMPSIMB == "=="):
            return BinaryNode('==', p.COMPOP, p.ADDOP).value
            #return p.COMPOP == p.ADDOP
        elif(p.COMPSIMB == "<="):
            return BinaryNode('<=', p.COMPOP, p.ADDOP).value
            #return p.COMPOP <= p.ADDOP
        elif(p.COMPSIMB == ">="):
            return BinaryNode('>=', p.COMPOP, p.ADDOP).value
            #return p.COMPOP >= p.ADDOP
        elif(p.COMPSIMB == "!="):
            return BinaryNode('!=', p.COMPOP, p.ADDOP).value
            #return p.COMPOP != p.ADDOP

    @_('ADDOP')                             #compOp = addOp
    def COMPOP(self,p):
        return p.ADDOP


    @_('ADDOP "+" PRODOP')                  #addOp = addOp + prodOp
    def ADDOP(self,p):
        pass
        return BinaryNode('+', p.ADDOP, p.PRODOP).value
        #return p.ADDOP + p.PRODOP

    @_('ADDOP "-" PRODOP')                  #addOp = addOp - prodOp
    def ADDOP(self,p):
        pass
        return BinaryNode('-', p.ADDOP, p.PRODOP).value
        #return p.ADDOP-p.PRODOP

    @_('PRODOP')                            #addOp = prodOp
    def ADDOP(self,p):
        pass
        return p.PRODOP


    @_('PRODOP "*" PAROP')                  #prodOp = prodOp * parOp
    def PRODOP(self,p):
        pass
        return BinaryNode('*', p.PRODOP, p.PAROP).value
        #return p.PRODOP * p.PAROP

    @_('PRODOP "/" PAROP')                  #prodOp = prodOp / parOp
    def PRODOP(self,p):
        pass
        return BinaryNode('/', p.PRODOP, p.PAROP).value
        #return p.PRODOP / p.PAROP
        
    ##
    ## PARENTHESES
    ## 
    @_('PAROP')                             #prodOp = parOp
    def PRODOP(self,p):
        return p.PAROP


    @_('"(" OROP ")"')                      #parOp = (orOp)
    def PAROP(self,p):
        return p.OROP

    ##
    ## TERMINAL SYMBOLS
    ##
    @_('VAL')                               #parOp = val
    def PAROP(self,p):
        return p.VAL

    @_('NUMBER')                            #val = NUMBER
    def VAL(self,p):
        print("movl $("+str(p.NUMBER)+"), %eax;\npushl %eax")
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
            print("movl "+str(+self.Table[self.ambito][1][p.ID][2])+"(%ebp),%eax;\npushl %eax;")
            return self.Table[self.ambito][1][p.ID][2]
        except:
            raise Exception("Variable '"+p.ID+"' undefined") 
    @_('REFERENCE')
    def VAL(self,p):
        pass       
    @_('"&" ID')
    def REFERENCE(self,p):
        try:
            print("leal "+str(self.Table[self.ambito][1][p.ID][2])+"(%ebp),%eax;\npushl %eax;\n")
            return p.ID
        except:
            raise Exception("Variable '"+p.ID+"' undefined") 
        


    
if __name__ == '__main__':
    lexer = CLexer()
    parser = CParser()
    text = ""
    #try:
    with open('input.txt',"r") as f:
        text = f.read()
        f.close()

    print("-----INPUT CODE-----")
    print(text)
    print("--------------------")
    print("")

    result = parser.parse(lexer.tokenize(text))
    print(result)
    print(parser.Table)
    #except Exception as e:
    #    print("[ERROR] " + str(e))

