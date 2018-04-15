import lex as lex
# names of tokens defined in a list of token
tokens = (
   'NUMBER',
   'PLUS',
   'MINUS',
   'TIMES',
   'DIVIDE',
   'SEMICOLON',
   'EQUALS',
   'TYPEINT',
   'TYPESTRING',
   'STRING',
   'TYPEBOOL',
   'BINARY',
   'BOOL',
   'ANDOR',
   'CIN',
   'DLA',
   'DRA',
   'COUT',
   'NAME',
   'ENDL',
   'LPAREN',
   'RPAREN',
   'IF',
   'ELSEIF',
   'ELSE',
   'RCURLY',
   'LCURLY',
   'WHILE',
   'MAIN',
)
# reserved words are used to prevent parser from interpreting words like 'if' as variables
reserved = {
   'if'    : 'IF',
   'elseif': 'ELSEIF',
   'then'  : 'THEN',
   'else'  : 'ELSE',
   'while' : 'WHILE',
   'cout'  : 'COUT',
   'cin'   : 'CIN',
   'endl'  : 'ENDL',
   'main'  : 'MAIN',
   '(true|false)' :'BOOL',
   '(\&\&|\|\|)' : 'ANDOR',
   '<<'    : 'DLA',
}
# precedence defined for arithmetic operation
precedence = ( 
    ('left','PLUS','MINUS'), 
    ('left','TIMES','DIVIDE'), 
    ('right','UMINUS'), 
    )
# Regular expression for simple tokens
t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_LPAREN  = r'\('
t_EQUALS  = r'='
t_RPAREN  = r'\)'
t_STRING  = r'"[^"]*"'
t_ANDOR   = r'(\&\&|\|\|)'
t_ENDL    = r'endl'
t_COUT    = r'cout'
t_CIN     = r'cin'
t_MAIN    = r'main'
t_SEMICOLON= r';'
t_RCURLY  = r'}'
t_LCURLY  = r'{'

# A regular expression rule with some action code


def t_DLA(t):
    r'<<'
    return t
def t_DRA(t):
    r'>>'
    return t
def t_BINARY(t):
    r'(<=|>=|>|<|==)'
    t.type = reserved.get(t.value,'BINARY')
    return t


def t_NUMBER(t):
    r'\d+'
    try:
        t.value = int(t.value)
    except ValueError:
        print "Line %d: Number %s is too large!" % (t.lineno,t.value)
        t.value = 0
    return t
def t_WHILE(t):
    r'while'
    return t
def t_IF(t):
    r'if'
    return t
def t_ELSEIF(t):
    r'elseif'
    return t
def t_ELSE(t):
    r'else'
    return t
def t_BOOL(t):
    r'(true|false)'
    return t

def t_TYPEINT(t):
    r'(int)'
    return t
def t_TYPESTRING(t):
    r'string'
    return t
def t_TYPEBOOL(t):
    r'bool'
    return t

def t_NAME(t):
    r'[a-z,A-Z_][a-z,A-Z,0-9_]*'
    t.type = reserved.get(t.value,'NAME')
    return t
# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
def t_endOfFile(t):
    r'\r+'
# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t'

# Error handling rule
def t_error(t):
    print "Illegal character '%s'" % t.value[0]
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()

import yacc as yacc

names = {}
# from here we start to create a tree structure of the code so that we can interpret it later
def p_main_start(p):
    'mainstart : TYPEINT MAIN LPAREN RPAREN LCURLY code RCURLY'
    p[0] = ('main',p[6])

def p_code_start(p):
    '''code :  cinsomething code
            |  coutsomething code
            |  assignment code
            |  ifstart code
            |  whilestart code'''
    p[0] = ('normalcode',p[1],p[2])

def p_while_start(p):
    'whilestart : WHILE LPAREN expressionBool RPAREN LCURLY code RCURLY'
    p[0] = ('while',p[3],p[6])
def p_if_start(p):
    'ifstart : IF LPAREN expressionBool RPAREN LCURLY code RCURLY elseIfstart'
    p[0] = ('if',p[3],p[6],p[8])

def p_elseIf_start(p):
    'elseIfstart : ELSEIF LPAREN expressionBool RPAREN LCURLY code RCURLY elseIfstart'
    p[0] = ('elseif',p[3],p[6],p[8])

def p_elseIf_start2(p):
    'elseIfstart : elsestart'
    p[0] = ('elseif',('TRUTHVALUE','false'),None,p[1])

def p_else_start(p):
    'elsestart  : ELSE LCURLY code RCURLY'
    p[0] = ('else',('TRUTHVALUE','true'),p[3])
def p_else_end(p):
    'elsestart : '
    p[0] = ('else',('TRUTHVALUE','false'),None)


def p_code_end(p):
    'code   : '
    p[0] = ('endcode',None)
def p_cin_input(p):
    'cinsomething : CIN cinContinue'
    p[0] = ('cin',p[2])
def p_cin_Continue(p):
    'cinContinue  : DRA NAME cinContinue'
    p[0] = ('cinNext',('NAME',p[2]),p[3])
def p_cin_end(p):
    'cinContinue : SEMICOLON'
    p[0] = ('Cend',None)
def p_cout_printable(p):
    'coutsomething  : COUT printable'
    p[0] = ('cout',p[2])
def p_printable_something(p):
    '''printable : DLA expression printable
                 | DLA expressionBool printable
                 | DLA expressionStr printable'''
                 # | DLA NAME printable'''
    p[0] = ('coutNext',p[2],p[3])
def p_printable_something2(p):
    'printable : DLA NAME printable'
    p[0] = ('coutNext',('NAME',p[2]),p[3])
def p_printable_end(p):
    'printable : DLA ENDL SEMICOLON'
    p[0] = ('Cend',None)
def p_reAssign_number(p):
    '''assignment : NAME EQUALS expression SEMICOLON
                  | NAME EQUALS expressionStr SEMICOLON
                  | NAME EQUALS expressionBool SEMICOLON'''
    p[0] = ('reassignment',p[3][0],p[1] , p[3])
def p_assign_first(p):
    '''assignment : TYPEINT NAME EQUALS expression SEMICOLON
                  | TYPESTRING NAME EQUALS expressionStr SEMICOLON
                  | TYPEBOOL NAME EQUALS expressionBool SEMICOLON'''
    p[0] = ('assignment',p[1],p[2] , p[4])

def p_assign_first2(p):
    '''assignment : TYPEINT NAME SEMICOLON
                  | TYPESTRING NAME SEMICOLON
                  | TYPEBOOL NAME SEMICOLON'''
    p[0] = ('assignment',p[1],p[2],None)

def p_expression_math(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression'''
    if p[2] == '+' : p[0] = ('PLUS',p[1],p[3])
    elif p[2] == '-': p[0] = ('MINUS',p[1],p[3])
    elif p[2] == '*': p[0] = ('TIMES',p[1],p[3])
    elif p[2] == '/': p[0] = ('DIVIDE',p[1],p[3])

def p_expression_number(p):
    'expression : NUMBER'
    p[0] = ('NUMBER',p[1])
def p_expression_name(p):
    'expression : NAME'
    p[0] = ('NAME',p[1])

def p_expression_string(p):
    'expressionStr : STRING'
    p[0] = ('STRINGVALUE',p[1])

def p_expression_bool(p):
    'expressionBool : BOOL'
    p[0] = ('TRUTHVALUE',p[1])

def p_expression_paren(p):
    'expression : LPAREN expression RPAREN'
    p[0] = ('ParenNUMBER',p[2])

def p_expression_parenStr(p):
    'expressionStr : LPAREN expressionStr RPAREN'
    p[0] = ('ParenSTRING',p[2])

def p_expression_append(p):
    'expressionStr : expressionStr PLUS expressionStr'
    if p[2] == '+' : p[0] = ('concat',p[1],p[3])

def p_expression_binMath(p):
    '''expressionBool : expression BINARY expression
                      | expressionBool ANDOR expressionBool'''
    p[0] = (p[2],p[1],p[3])

def p_expression_binMath(p):
    '''expressionBool : expression BINARY expression
                      | expressionBool ANDOR expressionBool'''
    p[0] = (p[2],p[1],p[3])


def p_expression_parenBool(p):
    'expressionBool : LPAREN expressionBool RPAREN'
    p[0] = ('ParenBOOL',p[2])

def p_expression_uminus(p):
    'expression : MINUS expression %prec UMINUS' 
    p[0] = -p[2]

def p_error(p):
    print "Syntax error in input!", p

# Build the parser
yacc.yacc()
# a dictionary of dictionary to keep variables in a scope
variablecounter = 0
emptyDict = {}

ListOfDict = []
ListOfDict.append(emptyDict)
while(1):
    s = raw_input('press Enter to Continue')
    inputFile = open('test.txt', 'r')
    lines = inputFile.readlines()
    code = ''.join(lines)
    result = yacc.parse(code)
    # result = yacc.parse('int main(){int j = 0;cin>>j;while(j<10){j=j+10;}cout<<j<<endl;}')
    #print result

    def initialize(key,variablecounter,inputVarCounter):
        if key not in variableArray[inputVarCounter]:
            variableArray[inputVarCounter][key] = -214124125
        else:
            print "Error: {0} already Declared!".format(key)
    
    def initialize(key,inputId,typeInput):
        if key not in ListOfDict[inputId]:
            ListOfDict[inputId][key] = []
            ListOfDict[inputId][key].append(typeInput)
            ListOfDict[inputId][key].append('210401211')
        else:
            print "Error: {0} already declared!".format(key)
    def assignVal(key,inputId,inputVal):
        if key in ListOfDict[inputId]:
            ListOfDict[inputId][key][1]=inputVal
        else:
            print "Error: {0} not declared!".format(key)

    def getValue(inputName,inputId):
        for i in range(inputId, -1, -1):
            
            if inputName in ListOfDict[i]:
                return ListOfDict[i][inputName]
        print "Error: {0} not declared!".format(inputName)
    def setValue(inputName,inputId):
        for i in range(inputId, -1, -1):
            if inputName in ListOfDict[i]:
                tempInput = raw_input('')
                try:
                    ListOfDict[i][inputName][1]=int(tempInput)
                except:
                    ListOfDict[i][inputName][1]=tempInput
                return
        print "Error: {0} not declared!".format(inputName)
    def setValue2(inputName,inputId,tempInput):
        for i in range(inputId, -1, -1):
            if inputName in ListOfDict[i]:
                # tempInput = raw_input('')
                ListOfDict[i][inputName][1]=tempInput
                return
        print "Error: {0} not declared!".format(inputName)
    def interpret2(p_tree,dictId):
        if(p_tree[0]) == 'endcode':
            ListOfDict[dictId] = {}
            return
        elif(p_tree[0]) == 'normalcode':
            dictId = dictId+1
            ListOfDict.append(emptyDict)
            interpret2(p_tree[1],dictId)
            interpret2(p_tree[2],dictId)
        elif(p_tree[0]) == 'assignment':
            initialize(p_tree[2],dictId,p_tree[1])
            tempValue = interpret2(p_tree[3],dictId)
            # print tempValue
            tempValue2 = tempValue
            if(p_tree[1]=='int'):
                tempValue2 = int(tempValue)
            assignVal(p_tree[2],dictId,tempValue2)
            # print p_tree
        elif(p_tree[0]) == 'reassignment':
            tempValue = interpret2(p_tree[3],dictId)
            setValue2(p_tree[2],dictId,tempValue)
        elif(p_tree[0]) == 'NUMBER':
            return p_tree[1]
        elif(p_tree[0]) == 'NAME':
            return getValue(p_tree[1],dictId)[1]
        elif(p_tree[0]) == 'PLUS':
            return (interpret2(p_tree[1],dictId)+interpret2(p_tree[2],dictId))
        elif(p_tree[0]) == 'TIMES':
            return (interpret2(p_tree[1],dictId)*interpret2(p_tree[2],dictId))
        elif(p_tree[0]) == 'DIVIDE':
            return (interpret2(p_tree[1],dictId)/interpret2(p_tree[2],dictId))
        elif(p_tree[0]) == 'MINUS':
            return (interpret2(p_tree[1],dictId)-interpret2(p_tree[2],dictId))
        elif(p_tree[0]) == 'TRUTHVALUE':
            if(p_tree[1])=='true':
                return True
            else:
                return False
        elif(p_tree[0]) == '&&':
            truthvalue1 = interpret2(p_tree[1],dictId)
            truthvalue2 = interpret2(p_tree[2],dictId)
            return (truthvalue1 and truthvalue2)
        elif(p_tree[0]) == '||':
            truthvalue1 = interpret2(p_tree[1],dictId)
            truthvalue2 = interpret2(p_tree[2],dictId)
            return (truthvalue1 or truthvalue2)
        elif(p_tree[0] == '<'):
            value1 = interpret2(p_tree[1],dictId)
            value2 = interpret2(p_tree[2],dictId)
            # print value1
            # print value2
            return int(value1)<int(value2)
        elif(p_tree[0] == '>'):
            value1 = interpret2(p_tree[1],dictId)
            value2 = interpret2(p_tree[2],dictId)
            return int(value1)>int(value2)
        elif(p_tree[0] == '<='):
            value1 = interpret2(p_tree[1],dictId)
            value2 = interpret2(p_tree[2],dictId)
            return int(value1)<=int(value2)
        elif(p_tree[0] == '>='):
            value1 = interpret2(p_tree[1],dictId)
            value2 = interpret2(p_tree[2],dictId)
            return int(value1)>=int(value2)
        elif(p_tree[0] == '=='):
            value1 = interpret2(p_tree[1],dictId)
            value2 = interpret2(p_tree[2],dictId)
            return int(value1)==int(value2)
        elif(p_tree[0] == 'STRINGVALUE'):
            return p_tree[1]
        elif(p_tree[0] == 'concat'):
            string1 = interpret2(p_tree[1],dictId)
            string2 = interpret2(p_tree[2],dictId)
            return string1[:-1] + string2[1:]
        elif(p_tree[0] == 'cout'):
            interpret2(p_tree[1],dictId)
        elif(p_tree[0])== 'cend':
            return None
        elif(p_tree[0] == 'coutNext'):
            thing1 = interpret2(p_tree[1],dictId)
            if(thing1 != None):
                print thing1
            thing2 = interpret2(p_tree[2],dictId)
        elif(p_tree[0] == 'cin'):
            interpret2(p_tree[1],dictId)
        elif(p_tree[0] == 'cinNext'):
            variableName = p_tree[1][1]
            # print variableName
            setValue(variableName,dictId)
        elif(p_tree[0]=='if'):
            truthvalueif = interpret2(p_tree[1],dictId)
            if(truthvalueif==True):
                tempDict = {}
                ListOfDict.append(tempDict)
                interpret2(p_tree[2],dictId+1)
            else:
                interpret2(p_tree[3],dictId)
        elif(p_tree[0]=='elseif'):
            truthvalueif = interpret2(p_tree[1],dictId)
            if(truthvalueif==True):
                tempDict = {}
                ListOfDict.append(tempDict)
                interpret2(p_tree[2],dictId+1)
            else:
                interpret2(p_tree[3],dictId)
        elif(p_tree[0]=='else'):
            truthvalueif = interpret2(p_tree[1],dictId)
            if(truthvalueif==True):
                tempDict = {}
                ListOfDict.append(tempDict)
                interpret2(p_tree[2],dictId+1)
        elif(p_tree[0] == 'while'):
            tempDictWhile = dictId+1
            tempDict = {}
            ListOfDict.append(tempDict)
            while(interpret2(p_tree[1],dictId)):
                interpret2(p_tree[2],tempDictWhile)
        elif(p_tree[0] == 'main'):
            interpret2(p_tree[1],dictId)
    (interpret2(result,0))
