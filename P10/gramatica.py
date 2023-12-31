from sly import Lexer
from sly import Parser
NE=1 #Current tag number

class BinaryNode():
    def __init__(self, op, p1, p2, parser=None):
        global NE
        ##
        ##Logical operations
        ##
        if(op=='and'):
            self.value=f"{p1}cmpl $0, %eax\n je Salto{NE}\n{p2}\n cmpl $0, %eax\n Salto:{NE}\n"
            NE += 1
        elif(op=='or'):
            self.value=f"{p1}cmpl $0, %eax\n je Salto{NE}\n{p2}\n cmpl $0, %eax\n Salto:{NE}\n"
            NE += 1
        elif(op=='=='):
            self.value=f"{p1}\npushl %eax\n{p2}\nmovl %eax,%ebx\npopl %eax\ncmpl %ebx,%eax\njne false{NE}\nmovl $1,%eax\nj final{NE}\nfalse{NE}:\nmovl $0,%eax\nfinal{NE}:\n"
            NE += 1
        elif(op=='!='):
            self.value=f"{p1}\npushl %eax\n{p2}\nmovl %eax,%ebx\npopl %eax\ncmpl %ebx,%eax\nje false{NE}\nmovl $1,%eax\nj final{NE}\nfalse{NE}:\nmovl $0,%eax\nfinal{NE}:\n"
            NE += 1
        elif(op=='>='):
            self.value=f"{p1}\npushl %eax\n{p2}\nmovl %eax,%ebx\npopl %eax\ncmpl %ebx,%eax\njl false{NE}\nmovl $1,%eax\nj final{NE}\nfalse{NE}:\nmovl $0,%eax\nfinal{NE}:\n"
            NE += 1
        elif(op=='<='):
            self.value=f"{p1}\npushl %eax\n{p2}\nmovl %eax,%ebx\npopl %eax\ncmpl %ebx,%eax\njg false{NE}\nmovl $1,%eax\nj final{NE}\nfalse{NE}:\nmovl $0,%eax\nfinal{NE}:\n"
            NE += 1
        elif(op=='<'):
            self.value=f"{p1}\npushl %eax\n{p2}\nmovl %eax,%ebx\npopl %eax\ncmpl %ebx,%eax\njge false{NE}\nmovl $1,%eax\nj final{NE}\nfalse{NE}:\nmovl $0,%eax\nfinal{NE}:\n"
            NE += 1
        elif(op=='>'):
           self.value=f"{p1}\npushl %eax\n{p2}\nmovl %eax,%ebx\npopl %eax\ncmpl %ebx,%eax\njle false{NE}\nmovl $1,%eax\nj final{NE}\nfalse{NE}:\nmovl $0,%eax\nfinal{NE}:\n"
           NE += 1

        ##
        ##Arithmetic operations
        ##
        elif(op=='+'):
            self.value=p1+"\npushl %eax\n"+p2+"\nmovl %eax, %ebx\npopl %eax\naddl %ebx,%eax\n"
        elif(op=='-'):
                self.value=p1+"\npushl %eax\n"+p2+"\nmovl %eax, %ebx\npopl %eax\nsubl %ebx,%eax\n"
        elif(op=='*'):
            self.value=p1+"\npushl %eax\n"+p2+"\nmovl %eax,%ebx\npopl %eax\nimmull %ebx,%eax\n"
        elif(op=='/'):
            self.value=p1+"\npushl %eax\n"+p2+"\nmovl %eax,%ebx\npopl %eax\ncdq\ndivl %ebx\n"

        ##
        ##Assignment
        ##
        elif(op=='asig'):
            try:
                ebpoffset = parser.Table[parser.ambito][1][p1][1]
                self.value = f"{p2}movl %eax, {ebpoffset}(%ebp)\n"
            except:
                self.value =p2+"movl %eax, " + p1+"\n"

        ##
        ##Declaration
        ##
        elif(op=='declar'):
            self.value = f"subl ${-1*parser.ebpOffset}, %esp\n{p2}"


        elif(op=='if'):
            self.value = f"{p1}cmpl $0,%eax\nje false{NE}\n{p2[0]}jmp final{NE}\nfalse{NE}:\n{p2[1]}\nfinal{NE}:\n"
            NE += 1
            
        elif(op=='while'):
            self.value = f"start{NE}:\n{p1}cmpl $0,%eax\nje final{NE}\n{p2}jmp start{NE}\nfinal{NE}:\n"
            NE += 1

        elif(op=='print'):
            self.value=""
            percents=p2.count("%d")
            if(p1):
                vars=len(p1)
            else:
                vars = 0
                L = []
            if(vars!=percents): 
                raise Exception("Too many variables in printf")
            else:
                for var in p1:
                        self.value+=var+" \n pushl %eax\n"
                self.value+="pushl "+p2+"\n"
                self.value+="Call printf\n"
                self.value+=f"addl ${(vars+1)*4},%esp\n"

        elif(op=='scanf'):
            self.value=""
            percents=p2.count("%d")
            vars=len(p1)
            if vars!=percents:
                raise Exception("Too many variables in scanf")
            for var in p1:
                self.value+=var+" \n pushl %eax\n"
            self.value+="pushl "+p2+"\n"
            self.value+="Call scanf\n"
            self.value+=f"addl ${(vars+1)*4},%esp\n"

        elif (op=='fcall'):
            parameters = getParameters(parser.Table[p1][1])
            print("p1: "+str(p1))
            print(str(p2[0]) + " ----- " + str(parameters))
            if(p2[0] != parameters):
                raise Exception("Incorrect parameters when calling: " + p1)  

            if(not p2):
                self.value="Call "+p1+"\n"
            else:
                self.value = ""
                for iarg in reversed(range(len(p2[1]))):
                    self.value+= f"{p2[1][iarg]}pushl %eax\n"
                self.value+=f"Call {p1}\naddl ${len(p2[1])*4},%esp\n"


#returns a list of the parameter types
def getParameters(variables):
    parameters = []
    for var in variables:
        if(variables[var][1]>=8):
            parameters.append(variables[var][0])

    return parameters

        


class UnaryNode():
    def __init__(self, op, p1):
        if(op=='not'):
            self.value = f"cmpl %0,%eax\nje false{NE}\nmovl $0,%eax\nj final{NE}\nfalse{NE}:\nmovl $1,%eax\nfinal{NE}:\n"







class CLexer(Lexer):
    
    tokens = {NUMBER,NUMBERF,CHAR, ID, TYPE,VOIDTYPE, COMPSIMB, ANDSIMB, ORSIMB,MAIN,PRINT,SCANF, STRING, IF, ELSE, WHILE, RETURN}

    # Ignored characters
    ignore = ' \t'

    literals = { ';', '(', ')', '=', '<', '>', '!', "+", "-", "*", "/", ',','{','}', '&', '[', ']'}

    # Regular expression rules for tokens
    ID = r'(?!int\b|float\b|char\b|void\b|main\b|printf\b|scanf\b|if\b|else\b|while\b|return\b|\[|\])[a-zA-Z_][a-zA-Z0-9_]*'
    
    COMPSIMB = r'==|<=|>=|!=|<|>'
    ORSIMB = r'\|\|'
    ANDSIMB =r'\&\&'
    TYPE = r'int|float|char'
    VOIDTYPE = r'void'
    
    MAIN = r'main'
    PRINT= r'printf'
    SCANF=r'scanf'
    IF = r'if'
    ELSE = r'else'
    WHILE = r'while'
    RETURN = r'return'


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
    Table=dict()    #LocalTable Structure: {funcName: [funcType, {varName: [vartype, varEbpOffset]}, {otherVars...}], [otherFunc...]}
    GlobalTable={}  #GlobalTable Structure: {varName: varType, varName2: varType2, ...}
    ambito="0"      #0 indicates global scope
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
        print(p.LINES)

    @_("")
    def emptymain(self,p):
        self.ambito="main"
        self.ebpOffset = 0
        self.Table[self.ambito]=["int",dict()]
        print(f".text\n.globl main\n.type main, @function\nmain:\n\n")
        print("pushl %ebp   #"+self.ambito+" PROLOGUE")
        print("movl %esp, %ebp\n")
        pass
        
    @_('S2 FUNCTION')
    def S2(self,p):
        pass

    @_('S2 GLOBALDECLAR')
    def S2(self,p):
        pass

    @_('S2 GLOBALASIG')
    def S2(self,p):
        pass
    
    @_('')
    def S2(self,p):
        pass
    
    

    @_('TYPE ID emptyF1 "(" ARGS ")" "{" LINES "}" emptyF2')
    def FUNCTION(self,p):
        print(p.LINES)

    @_('VOIDTYPE ID emptyF1 "(" ARGS ")" "{" LINES "}" emptyF2')
    def FUNCTION(self,p):
        print(p.LINES)

    @_('')
    def emptyF1(self,p):
        #function prologue
        self.ebpOffsetArg += 4
        self.ambito=p[-1]
        self.ebpOffset = 0
        self.Table[self.ambito]=[p[-1], dict(), self.ebpOffsetArg]
        print(f".text\n.globl {p[-1]}\n.type {p[-1]}, @function\n{p[-1]}:\n\n")
        print("pushl %ebp   #"+self.ambito+" PROLOGUE")
        print("movl %esp, %ebp\n")
        return p[-2]
        
    @_('')
    def emptyF2(self,p):
        self.ebpOffsetArg += 4
        self.ambito = "0"
        pass


    #--Global declarations--
    @_('TYPE ELEM emptyglobal emptyaux RESTGLOBAL ";"') 
    def GLOBALDECLAR(self,p):
        pass
    @_('"," emptyglobal2 ELEM RESTGLOBAL')
    def RESTGLOBAL(self,p):
        pass
    @_('')
    def RESTGLOBAL(self,p):
        pass
    @_('')
    def emptyglobal(self,p):
        return p[-2]
    @_('')
    def emptyglobal2(self,p):
        return p[-3]
    @_('')
    def emptyaux(self,p):
        pass



    #--Global assignments--
    @_('ID "=" INSTR ";"')
    def GLOBALASIG(self,p):
        try:
            value = p.INSTR
            self.GlobalTable[p.ID] = value
        except:
            raise Exception("Variable '"+p.ID+"' undefined")
        
        pass

    

    @_('TYPE REF ARG RARGS' )
    def ARGS(self,p):
        pass
    
    
    @_('')
    def ARGS(self,p):
        pass

    @_('"," TYPE REF ARG RARGS')
    def RARGS(self,p):
        pass

    @_('')
    def RARGS(self,p):
        pass

    @_('"*" REF')
    def REF(self,p):
        return "*" + p.REF

    @_('')
    def REF(self,p):
        return ""



    @_('ID')
    def ARG(self,p):
        try:
            self.ebpOffsetArg += 4
            self.Table[self.ambito][1][p.ID]=[p[-3]+p[-2], self.ebpOffsetArg]
        except (KeyError):
            self.GlobalTable[p.ID] = p[-3]+p[-2]
        return 

    

    @_('LINES LINE')                        #S = S line ';'
    def LINES(self, p):
        return f"{p.LINES}{p.LINE}"

    @_('')                                  #S = epsilon
    def LINES(self,p):
        return ""


    ##
    ## MAIN INPUT
    ##
    @_('INSTR ";"')                        #LINE = instr
    def LINE(self, p):
        return p.INSTR

    @_('DECLAR ";"')                        #LINE = declar
    def LINE(self, p):
        return p.DECLAR

    #RETURN
    #Return statements of the form: return a=2; are not considered,they may be accepted by the grammar, but their output will be incorrect
    #All functions must have a return statement (even void functions), if not, function epilogue wont be included in the output
    @_('RETURN INSTR ";"')
    def LINE(self, p):
        return f"#Save return value in %eax\n{p.INSTR}\nmovl %ebp %esp #{self.ambito} EPILOGUE\npopl %ebp\nret\n"

    @_('RETURN ";"')
    def LINE(self, p):
        return f"movl %ebp %esp #{self.ambito} EPILOGUE\npopl %ebp\nret\n"
        

    ##SCANF
    @_('SCANF "(" STRING SCANIDS ")" ";"')
    def LINE(self,p):
        L=list()
        L=p.SCANIDS
        s=p.STRING
        return BinaryNode("scanf", L, s).value         
            
    @_(", REFERENCE SCANIDS ")
    def SCANIDS(self,p):
        L=[]
        L.append(p.REFERENCE)
        
        L += p.SCANIDS
        return L

    @_("")
    def SCANIDS(self,p):
        return []


    ##PRINTF
    @_('PRINT "(" STRING PRINTIDS ")" ";"')
    def LINE(self, p):
        L=list()
        L=p.PRINTIDS
        s=p.STRING
        return BinaryNode("print",L,s).value
           
    
    @_('"," INSTR PRINTIDS')
    def PRINTIDS(self,p):
        L=[]
        L.append(p.INSTR)
        
        L += p.PRINTIDS
        return L
        
    @_('')
    def PRINTIDS(self,p):
        return []


    #if statements must use {} and end with ";". if there is an else, the 
    #";" must be after the else, not the if
    @_('IF "(" OROP ")" "{" LINES "}" ELSERULE')
    def LINE(self,p):
        L=[p.LINES,p.ELSERULE]
        print(BinaryNode("if",p.OROP[1],L,self).value)
        return BinaryNode("if",p.OROP[1],L,self).value
    @_('ELSE "{" LINES "}"')
    def ELSERULE(self,p):
        return p.LINES

    @_('')
    def ELSERULE(self,p):
        return ""



    #while statements must use {} and end with ";".
    @_('WHILE "(" OROP ")" "{" LINES "}"')
    def LINE(self,p):
        return BinaryNode("while",p.OROP[1],p.LINES).value



    ##
    ## LANGUAJE INSTRUCTIONS
    ##
    @_('ASIG')                              #instr = asig
    def INSTR(self,p):
        return p.ASIG

    @_('OROP')                              #instr = orOp
    def INSTR(self,p):
        return p.OROP[1]
        
    @_('FCALL')
    def INSTR(self,p):
        return p.FCALL
    

    @_('ID "(" FARGS ")"')
    def FCALL(self,p):
        id=p.ID
        L=(p.FARGS)
        return BinaryNode("fcall",id,L,self).value

    @_('FARG RFARGS' )
    def FARGS(self,p):
        types = [p.FARG[0]]
        parameters = [p.FARG[1]]
        if(p.RFARGS):
            types+=p.RFARGS[0]
            parameters += p.RFARGS[1]
        
        return [types, parameters]
    
    @_('')
    def FARGS(self,p):
        return ""

    @_('"," FARG RFARGS')
    def RFARGS(self,p):
        types = [p.FARG[0]]
        parameters = [p.FARG[1]]
        if(p.RFARGS):
            types+=p.RFARGS[0]
            parameters += p.RFARGS[1]

        return [types, parameters]
        
    @_('')
    def RFARGS(self,p):
        return []

    @_('VAL')
    def FARG(self,p):
        return p.VAL

    #DECLARATIONS
    @_('TYPE POINTERS IDPRIMA')
    def DECLAR(self,p):
        return BinaryNode("declar",p.TYPE,p.IDPRIMA, self).value

    @_('"*" POINTERS')
    def POINTERS(self,p):
        return p.POINTERS + "*"

    @_('')
    def POINTERS(self,p):
        return ''

    @_('empty ELEM REST')
    def IDPRIMA(self,p):
        return p.ELEM+"\n"+p.REST
        
    @_('"," empty2 ELEM REST')
    def REST(self,p):
        return p.ELEM+"\n"+p.REST

    @_('')
    def REST(self,p):
        return ""
        
    @_('ID ARRAY')
    def ELEM(self,p):
        arraySizes = p.ARRAY
        if (len(arraySizes) > 0):
            arrayElements = 1
            for dim in arraySizes:
                arrayElements *= dim

            #Adjust ebpOffset (4 per array element, -4 that an element already takes)
            self.ebpOffset -= ((4*arrayElements)-4)

            self.Table[self.ambito][1][p.ID] =[p[-4]+p[-3]+("[]"*len(arraySizes)), self.ebpOffset]
        else:
            pointerType = ""
            if(p[-4] and "*" in p[-4]):
                pointerType = p[-4]
            
            try:
                self.Table[self.ambito][1][p.ID] =[p[-3]+pointerType, self.ebpOffset]
            except (KeyError):
                self.GlobalTable[p.ID] =p[-3]+pointerType
        return ""


    @_('"[" NUMBER "]" ARRAY')
    def ARRAY(self,p):
        arraySizes = p.ARRAY
        arraySizes.append(p.NUMBER)
        return arraySizes

    @_('')
    def ARRAY(self,p):
        return []

    
    #DECLARATION INITIALIZATION
    @_('ID "=" INSTR')
    def ELEM(self,p):
        valueType = p[-4]
        try:
            self.Table[self.ambito][1][p.ID]= [valueType, self.ebpOffset]
        except (KeyError):
            self.GlobalTable[p.ID] = valueType
        return BinaryNode("asig", p.ID, p.INSTR, self).value

    #INHERITANCE SIMULATION
    @_('')
    def empty(self, p):
        self.ebpOffset-=4
        
        return p[-2]

    @_('')
    def empty2(self, p):
        self.ebpOffset-=4
        return p[-3]



    #ASSIGNMENTS
    @_('ID "=" INSTR')                 #asig = ID '=' instr
    def ASIG(self,p):
        if p.ID in self.Table[self.ambito][1]:
            return BinaryNode("asig", p.ID, p.INSTR, self).value
        elif p.ID in  self.GlobalTable:
            return BinaryNode("asig", p.ID, p.INSTR, self).value
        else:
            raise Exception("Variable '"+p.ID+"' undefined")
        



    ##
    ## ARITMETICAL OPERATIONS
    ##
    @_('OROP ORSIMB ANDOP')                 #orOp = orOp '||' andOp
    def OROP(self,p):
        if(p.OROP[0] == p.ANDOP[0]):
            return (p.OROP[0], BinaryNode("or",p.OROP[1],p.ANDOP[1]).value)
        else:
            raise Exception("Incorrect types when doing OR operation")

    @_('ANDOP')                             #orOp = andOp
    def OROP(self,p):
        return p.ANDOP


    @_('ANDOP ANDSIMB NOTOP')               #andOp = andOp '&&' notOp
    def ANDOP(self,p):
        if(p.ANDOP[0] == p.NOTOP[0]):
            return BinaryNode("and", p.ANDOP[1], p.NOTOP[1]).value
        else:
            raise Exception("Incorrect types when doing AND operation")

    @_('NOTOP')                             #andOp = notOp
    def ANDOP(self,p):
        return p.NOTOP


    @_('"!" NOTOP')                         #notOp = '!' notOp
    def NOTOP(self,p):
        return (p.NOTOP[0], UnaryNode("not", p.NOTOP[1]).value)

    @_('COMPOP')                            #notOp = compOp
    def NOTOP(self,p):
        return p.COMPOP


    @_('COMPOP COMPSIMB ADDOP')             #compOp = compOp compSimb addOp
    def COMPOP(self,p):
        if(p.COMPOP[0] == p.ADDOP[0]):
            return (p.COMPOP[0], BinaryNode(p.COMPSIMB, p.COMPOP[1], p.ADDOP[1]).value)
        else:
            raise Exception("Incorrect types when doing comparison")

    @_('ADDOP')                             #compOp = addOp
    def COMPOP(self,p):
        return p.ADDOP


    @_('ADDOP "+" PRODOP')                  #addOp = addOp + prodOp
    def ADDOP(self,p):
        if(p.ADDOP[0] == p.PRODOP[0]):
            return (p.ADDOP[0], BinaryNode('+', p.ADDOP[1], p.PRODOP[1]).value)
        else:
            raise Exception("Incorrect types when doing sum")

    @_('ADDOP "-" PRODOP')                  #addOp = addOp - prodOp
    def ADDOP(self,p):
        if(p.ADDOP[0] == p.PRODOP[0]):
            return (p.ADDOP[0], BinaryNode('-', p.ADDOP[1], p.PRODOP[1]).value)
        else:
            raise Exception("Incorrect types when doing substraction")

    @_('PRODOP')                            #addOp = prodOp
    def ADDOP(self,p):
        return p.PRODOP


    @_('PRODOP "*" PAROP')                  #prodOp = prodOp * parOp
    def PRODOP(self,p):
        if(p.PRODOP[0] == p.PAROP[0]):
            return (p.PRODOP[0], BinaryNode('*', p.PRODOP[1], p.PAROP[1]).value)
        else:
            raise Exception("Incorrect types when doing product")

    @_('PRODOP "/" PAROP')                  #prodOp = prodOp / parOp
    def PRODOP(self,p):
        if(p.PRODOP[0] == p.PAROP[0]):
            return (p.PRODOP[0], BinaryNode('/', p.PRODOP[1], p.PAROP[1]).value)
        else:
            raise Exception("Incorrect types when doing division")

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
        return ("int", f"movl $({p.NUMBER}), %eax\n")

    @_('NUMBERF')                            #val = NUMBERF
    def VAL(self,p):
        return ("float", p.NUMBERF)

    @_('CHAR')                            #val = CHAR
    def VAL(self,p):
        return ("char", p.CHAR)

    @_('ID')                                #val = ID
    def VAL(self,p):
        try:
            return (self.Table[self.ambito][1][p.ID][0],f"movl {+self.Table[self.ambito][1][p.ID][1]}(%ebp),%eax\n")
        except:
            if(p.ID in self.GlobalTable):
                return (self.GlobalTable[p.ID], f"movl {p.ID}, %eax\n")
            else:
                raise Exception("Variable '"+p.ID+"' undefined") 

    @_('REFERENCE')
    def VAL(self,p):
        return p.REFERENCE

    @_('"&" ID')
    def REFERENCE(self,p):
        try:
            return (self.Table[self.ambito][1][p.ID][0]+"*", f"leal {self.Table[self.ambito][1][p.ID][1]}(%ebp),%eax\n")
        except:
            if(p.ID in self.GlobalTable):
                return (self.GlobalTable[p.ID]+"*", f"leal {p.ID}, %eax\n")
            else:
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
    print("Global variables table: "+ str(parser.GlobalTable))
    print("Function variables table: " + str(parser.Table))
    #except Exception as e:
    #    print("[ERROR] " + str(e))
