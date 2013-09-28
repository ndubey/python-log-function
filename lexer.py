"""
######################################################################
#
#   @file
#    lexer.py
#   @brief
#    This is lexer for C it tokenizes the input file provided in C/C++
#    List of token is returned with token value and token type.
#
#   @detail
#    For each token a token type which is either Id, Reserved, Quotes
#
#   @author
#    nandan
#
#   Creation Date :
#
#   History
#   Modify information
#
######################################################################
"""

import os.path
import sys
from collections import deque

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


class lexer_state:
    def __init__(self):
        self.state = "Begin" #States can be $ begin ^ end id comment etc
    def get_state(self):
        return self.state
    def set_state(self,state):
        #print "old state: ",self.state," new state: ",state
        self.state=state;

class token:
    def check_reserved_c_type(self):
        if self.value in ['int','double','char','float','void','include']:
            return True
        return False
    def check_dbg_type(self):
        if self.value in ['print','printf','LOG','DATA_MSG','MESSAGE']:
            return True
        return False
    def get_type(self,value=""):
        if self.tok_type is not "Id":
            return self.tok_type
        if self.check_reserved_c_type():
            return "Reserved"    #identifier c reserved operator number
        if self.check_dbg_type():
          return "Debug"
        return "Id"              #default return id
    def __init__(self,value=None):
        self.value = value
        self.tok_type = None
    def set_value(self,value):
        self.value = value
    def append(self,to_append):
        if not self.value:
            self.value=""
        self.value = self.value+to_append
    def set_type(self,tok_type):
        self.tok_type  = tok_type
    def get_value(self):
        return self.value

class lexer:
    "A lexical analyzer class for simple shell-like syntaxes."
    def __init__(self, instream=None, infile=None):
        if isinstance(instream, basestring):
            instream = StringIO(instream)
        if instream is not None:
            self.instream = instream
            self.infile = infile
        else:
            self.instream = sys.stdin
            self.infile = None
        self.eof = ''
        self.macro               = '#'    #send state to macro reading #
        self.single_line_comment = '//'   #send state to single line comment s
        self.multiline_comment_start = '/*' #send state to multiline comment m
        self.multiline_comment_end = '*/'
        self.wordchars  = ('abcdfeghijklmnopqrstuvwxyz'
                          'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_')
        self.operator = ('<>=+-*')
        self.small_lbrace = '('
        self.small_rbrace = ')'
        self.curly_lbrace = '{'
        self.curly_rbrace = '}'
        self.whitespace = ' \t\r\n'
        self.whitespace_split = False
        self.quotes = '\'"'
        self.escape = '\\'
        self.escapedquotes = '"'
        self.state = lexer_state()
        self.pushback = deque()
        self.token    = token()
        self.next_token = token()
        self.lineno = 1
        self.debug = 2
        self.escaped = False
        self.filestack = deque()
        self.source = None
        self.lookahead = None

    def push_source(self, newstream, newfile=None):
        "Push an input source onto the lexer's input source stack."
        if isinstance(newstream, basestring):
            newstream = StringIO(newstream)
        self.filestack.appendleft((self.infile, self.instream, self.lineno))
        self.infile = newfile
        self.instream = newstream
        self.lineno = 1
        if self.debug:
            if newfile is not None:
                print 'lexer: pushing to file %s' % (self.infile,)
            else:
                print 'lexer: pushing to stream %s' % (self.instream,)

    def pop_source(self):
        "Pop the input source stack."
        self.instream.close()
        (self.infile, self.instream, self.lineno) = self.filestack.popleft()
        if self.debug:
            print 'lexer: popping to %s, line %d' \
                  % (self.instream, self.lineno)
        self.state.set_state("Begin");

    def get_token(self):
        "Get a token from the input stream (or from stack if it's nonempty)"
        #print "in func: get_token"
        if self.pushback:
            tok = self.pushback.popleft()
            if self.debug >= 1:
                print "lexer: popping token " + repr(tok.get_value())
            return tok
        # No pushback.  Get a token.
        raw = self.read_token()
        #print "in func: get_token after one read tok"
        # Handle inclusions
        if self.source is not None:
            print "source is not none"
            while raw == self.source:
                spec = self.sourcehook(self.read_token())
                if spec:
                    (newfile, newstream) = spec
                    self.push_source(newstream, newfile)
                raw = self.get_token()
        # Maybe we got EOF instead?
        while raw == self.eof:
            print "raw == self.eof"
            if not self.filestack:
                return self.eof
            else:
                self.pop_source()
                raw = self.get_token()
        # Neither inclusion nor EOF
        if self.debug >= 1:
            if raw.get_value() != self.eof:
                print "lexer: token=" + repr(raw)
            else:
                print "lexer: token=EOF"
        return raw

    def dump_lexer_state(self,inp=None):
      if self.debug > 3:
        print "lexer: Debug: State: ", self.state.get_state(), " lookahead: ", self.lookahead, " on char: ",inp

#call special function in case of { } ( ) "
    def read_token(self):
        if self.next_token.get_value():#if next token is already available
            self.token = token()
            self.token.set_value(self.next_token.get_value())
            self.token.set_type(self.next_token.get_type())
            self.next_token = token() #reset next token
            #reset state
            self.state.set_state("Begin")
            return self.token
        self.token = token() #brand new token
        quoted = False
        closing = None   #in case of quote
        while True:
            if self.lookahead:
                nextchar = self.lookahead
            else:
                nextchar = self.instream.read(1)
            self.lookahead = self.instream.read(1)

            if nextchar == '\n':
                self.lineno = self.lineno + 1
                if self.state == "MComment":
                    #nothing to do here
                    continue
            if self.debug >= 3:
                print "lexer: in state", repr(self.state.get_state()), \
                      "I see character:", repr(nextchar)
            self.dump_lexer_state(nextchar)                                       #print "Err: nextchar: ",nextchar
            if self.state.get_state() is "End":
                self.token.set_value('')        # past end of file
                break

            elif self.state.get_state() == "MComment":
                if nextchar == "*":
                    if self.lookahead == "/":
                        self.lookahead = self.instream.read(1)
                        self.state.set_state("Begin")
                #keep on eating everything
            elif self.state.get_state() == "SComment":
                #reset state if \n not escaped else keep initial state ' '
                if nextchar =='\n':
                  self.state.set_state("Begin")
                elif nextchar in self.escape:                                                           #Escape
                    #escape sequence detected: Continue as it is with next character
                    #skipped one character just after escape
                    self.lookahead = self.instream.read(1)
            elif nextchar == ';':                                                               #Semicolon: Reset state
                self.state.set_state("Begin")
                if self.token.get_value():
                    break   #emit whatever is there in token

            elif self.state.get_state() == "Quotes":                                             #State: Quotes
                quoted = True
                if not nextchar:      # end of file
                    if self.debug >= 333:
                        print "lexer: I see EOF in quotes state"
                    # XXX what error should be raised here?
                    raise ValueError, "No closing quotation"
                if nextchar == closing:
                        self.state.set_state("Begin")
                        break
                else:
                    self.token.append(nextchar)

            elif self.state.get_state() == "Begin":                                              #State: Begin
                if not nextchar:                                                                        #EOF
                    self.state.set_state("End")  # end of file
                    self.token.set_value(self.eof)
                    break
                elif nextchar in self.whitespace:                                                       #Whitespace
                    if self.debug >= 3:
                        print "lexer: I see whitespace in Begin state"
                    #eat whitespace
                elif nextchar in self.escape:                                                           #Escape
                    #escape sequence detected: Continue as it is with next character
                    #skipped one character just after escape
                    self.lookahead = self.instream.read(1)
                elif nextchar in self.single_line_comment:
                    if self.lookahead in self.single_line_comment:                                      #Single line comment
                        self.state.set_state("SComment")#Single line comment
                        self.lookahead = self.instream.read(1)
                    elif self.lookahead == '*':                                                         #Multiple line comment
                        self.state.set_state("MComment")#Multi line comment
                        self.lookahead = self.instream.read(1)
                    else: #division                                                                     #Division
                        self.set_state("Begin")
                        self.token.set_type("Div")
                        self.token.set_value(nextchar)
                        break#emit current token
                elif nextchar in self.operator:                                                         #Operators
                    if self.lookahead in self.operator:
                        #double operator
                        self.token.append(nextchar)
                        self.token.append(self.lookahead)
                        self.lookahead = self.instream.read(1)
                        self.token.set_type("DoubleOp")
                        break#emit double operator
                    else:
                        self.token.set_value(nextchar)
                        self.token.set_type("Op")
                        break#emit operator
                elif nextchar in self.wordchars:                                                             #Id
                    self.token.set_value(nextchar)
                    self.state.set_state("Id")
                    self.token.set_type("Id")
                    continue
                elif nextchar in self.quotes:                                                                #Quotes
                    self.state.set_state("Quotes")
                    self.token.set_type("Quotes")
                    closing = nextchar
                else:
                    self.token.set_value(nextchar)
                    break;#emit this character

            elif self.state.get_state() == 'Id':
                if not nextchar:
                    self.state.set_state(None)   # end of file
                    break
                elif nextchar in self.whitespace:
                    if self.debug >= 2:
                        print "lexer: I see whitespace in Id state"
                    self.state.set_state("Begin")
                    break   # emit current token
                elif nextchar in self.escape:                                                           #Escape
                    #escape sequence detected: Continue as it is with next character
                    #skipped one character just after escape
                    self.lookahead = self.instream.read(1)
                    self.state.set_state("Begin")
                    if self.debug >= 2:
                        print "lexer: Err: I see escape in Id state"
                    break #emit id
                elif nextchar in self.single_line_comment:
                    if self.lookahead in self.single_line_comment:                                      #Single line comment
                        self.state.set_state("SComment")#Single line comment
                        self.lookahead = self.instream.read(1)
                        if self.debug >= 2:
                            print "lexer: Err: I see Single line comment in Id state"
                    elif self.lookahead == '*':                                                         #Multiple line comment
                        self.state.set_state("MComment")#Multi line comment
                        self.lookahead = self.instream.read(1)
                        if self.debug >= 2:
                            print "lexer: Err: I see Single line comment in Id state"
                    else: #division                                                                     #Division
                        self.set_state("Begin")
                        if self.debug >= 2:
                            print "lexer: Err: I see div operator in Id state"
                        #save this to return in next call
                        self.next_token.set_type("Div")
                        self.token.set_value(nextchar)
                        break#emit current token
                elif nextchar in self.operator:                                                         #Operators
                    if self.lookahead in self.operator:
                        #double operator
                        #save this to return in next call
                        self.next_token.append(nextchar)
                        self.next_token.append(self.lookahead)
                        self.lookahead = self.instream.read(1)
                        self.next_token.set_type("DoubleOp")
                        if self.debug >= 2:
                            print "lexer: Err: I see operator in Id state"
                        break#emit double operator
                    else:
                        self.next_token.set_value(nextchar)
                        self.next_token.set_type("Op")
                        break#emit operator
                    self.state.set_state("Begin")
                elif nextchar in self.wordchars:                                                             #Id
                    self.token.append(nextchar)
                    continue
                elif nextchar in self.quotes:                                                                #Quotes
                    if self.debug >= 2:
                        print "lexer: Err: I see quotes in Id state"
                    self.state.set_state("Quotes")
                    closing = nextchar
                    break #emit current
                else:
                    self.next_token.set_value(nextchar)
                    self.state.set_state("Begin")
                    break;#emit this character
        return self.token

    def sourcehook(self, newfile):
        "Hook called on a filename to be sourced."
        if newfile[0] == '"':
            newfile = newfile[1:-1]
        # This implements cpp-like semantics for relative-path inclusion.
        if isinstance(self.infile, basestring) and not os.path.isabs(newfile):
            newfile = os.path.join(os.path.dirname(self.infile), newfile)
        return (newfile, open(newfile, "r"))

    def error_leader(self, infile=None, lineno=None):
        "Emit a C-compiler-like, Emacs-friendly error-message leader."
        if infile is None:
            infile = self.infile
        if lineno is None:
            lineno = self.lineno
        return "\"%s\", line %d: " % (infile, lineno)

    def __iter__(self):
        return self

    def next(self):
        token = self.get_token()
        if token.get_value() == self.eof:
            raise StopIteration
        return token

def split(s, comments=False, posix=True):
    lex = shlex(s, posix=posix)
    lex.whitespace_split = True
    if not comments:
        lex.commenters = ''
    return list(lex)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        lexer = shlex()
    else:
        file = sys.argv[1]
        lexer = shlex(open(file), file)
    while 1:
        tt = lexer.get_token()
        if tt:
            print "lexer Token: " + repr(tt)
        else:
            break
