"""
######################################################################
#
#   @file
#    parser.py
#   @brief
#    Find the Function and Log messages
#
#   @detail
#    For each function output the function declaration or id and then all
#    the log messages inside the function.
#    functions are defined as id( many ids but no braces ){
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
from lexer import lexer, token
import sys

class parser:
  def __init__(self):
    self.state = "Begin"
    self.func_name = ""
    self.func_arguments = ""
  def get_state(self):
    return self.state
  def set_state(self,state):
    print "parser: changing parser state from: ", self.state, " to: ",state
    self.state = state

class debug_msg:
  def __init__(self):
    self.macro_name = "" #not used
    self.message = ""
    self.args = ""
  def set_macro_name(self, macro_name):
    self.macroname = macro_name
  def get_macro_name(self):
    return self.macro_name
  def set_message(self, message):
    self.message = message
  def get_message(self):
    return self.message
  def get_macro_name(self):
    return self.macro_name
  def set_args(self, args):
    self.args = args
  def append_args(self,to_append):
    #combine %s if any which has constant string e.g. "%s","args"
    self.args += ","
    self.args += to_append
  def get_args(self):
    return self.args


class function:
  def __init__(self):
    self.name = ""
    self.args = ""
  def set_name(self, func_name):
    self.name = func_name
  def get_func_name(self):
    return self.name
  def set_args(self, args):
    self.args = args
  def append_args(self,to_append):
    #combine %s if any which has constant string e.g. "%s","args"
    self.args += ","
    self.args += to_append
  def get_args(self):
    return self.args

#dictionary of debug message followed by object which is
#sebug argument function name file name, function argument
#for same key we will use list
class value:
  def __init__(self):
    self.dbg_msg = None
    self.function = None
    self.next = None
  def set_function(self, function):
    self.function = function
  def get_function(self):
    return self.function
  def set_dbg_msg(self, dbg_msg):
    self.dbg_msg = dbg_msg
  def get_dbg_msg(self):
    return self.dbg_msg
  def get_next(self):
    return self.next
  def set_next(self,val):
    self.next = val

cmplt_msg_tbl = dict()
partial_msg_tbl = dict()
#list
rest = []

def num_args(msg):
  return msg.count('%')

def pos_first_arg_occ(msg):
  return msg.find('%')

def insert_in_list(table_entry,val):
  if table_entry.get_next == None:
    table_entry.set_next(val)
  else:
    insert_in_list(table_entry.get_next(),val)


def insert_in_tbl(dbg_msg,func):
  print "parser: ",dbg_msg.get_message()
  print "parser: ",func.get_func_name()
  val = value()
  val.set_function(func)
  val.set_dbg_msg(dbg_msg)
  val.set_next(None)
  pos = pos_first_arg_occ(dbg_msg.get_message())
  if num_args(dbg_msg.get_message()) == 0:
    print "parser: inserting in cmplt_msg_tbl "
    cmplt_msg_tbl[dbg_msg.get_message()] = val
  elif pos > 12:
    print "parser: inserting in partial_msg_tbl "
    if(partial_msg_tbl.get(dbg_msg.get_message()[:12],None) == None):
      partial_msg_tbl[dbg_msg.get_message()[:12]] = val;
    else:
      insert_in_list(partial_msg_tbl.get(dbg_msg.get_message()[:12],val))
  else:
    print "parser: inserting in rest "
    rest.append(val)

class parse:
  def __init__(self,filename):
    from lexer import lexer, token
    from parser import parser
    self.filename = filename
    print "parser: Lexing on file:", self.filename
    body = file(self.filename, 'rt').read()
    print 'parser: rORIGINAL:', repr(body)
    print
    print
    print 'parser: -------------TOKENS:------------------'
    lexer = lexer(body)
    parser = parser()
    func_name = None
    curly_brace = 0
    small_brace = 0
    args = ""
    for token in lexer:
      #first find a function name store id and lookahead if brace move to state
      print "parser: parsing token: ", token.get_value()," of type: ", token.get_type()
      if parser.get_state() == "Begin":
        print "parser: parser state Begin"
        if token.get_type() == "Id":
          parser.set_state("FuncName")
          func_name = token.get_value()
      elif parser.get_state() == "FuncName":
        type(token.get_value())
        type(token.get_type())
        if token.get_value() == "(":
          parser.set_state("FuncArgs")
        elif token.get_type() == "Id":
          parser.set_state("FuncName")
          func_name = token.get_value()
        else:
          parser.set_state("Begin")
      elif parser.get_state() == "FuncArgs":
        if token.get_value() == ")":
          parser.set_state("FuncBody")
        elif token.get_value() == ",":
          print "parser: Comma"
        elif token.get_type() == "Id":
          args+=token.get_value()
        else:
          print "parser: found: ", token.get_value()," while parser in state Args"
          #reset parser
          parser.set_state("Begin")
      elif parser.get_state() == "FuncBody":
        if token.get_value() == "{":
          #confirmed function update everything
          parser.set_state("Function")
          aFunction = function()
          aFunction.set_name(func_name)
          aFunction.set_args(args);
          print "parser: ***********Found a function by name : ", func_name, " **************************"
          curly_brace += 1
          #insert function
        elif token.get_type() == "Id":
          parser.set_state("FuncName")
          func_name = token.get_value()
        else:
          parser.set_state("Begin")
      elif parser.get_state() == "Function":
        if token.get_value() == "}":
          curly_brace -= 1
          if curly_brace == 0:
            print "parser: ********* Finished function: ",func_name ,"******************"
            #function ends update everything
            parser.set_state("Begin")
            #close messages for this func
        elif token.get_value() == "{":
          curly_brace += 1
        elif token.get_type() == "Debug":
          parser.set_state("Debug")
          dbg_msg = debug_msg()
          dbg_msg.set_macro_name(token.get_value())
        elif token.get_type() == "Entry/Exit":
          parser.set_state("DebugEntry/Exit")
          dbg_msg = debug_msg()
          dbg_msg.set_macro_name(token.get_value())
      elif parser.get_state() == "Debug":
        if token.get_value() == "(":
          if small_brace == 0:
            parser.set_state("DbgMsg")
          small_brace += 1
      elif parser.get_state() == "DbgMsg":
        if token.get_type() == "Quotes":
          dbg_msg.set_message(token.get_value())
        elif token.get_value() == ")":
          small_brace -= 1
          if small_brace == 0:
            print "parser: **** Finished one Debug message***** "
            insert_in_tbl(dbg_msg,aFunction);
            parser.set_state("Function")

        else:
          parser.set_state("DbgMsgArgs")

      elif parser.get_state() == "DbgMsgArgs":
        if token.get_value() == ")":
          small_brace -= 1
          if small_brace == 0:
            print "parser: **** Finished one Debug message***** "
            insert_in_tbl(dbg_msg,aFunction);
            parser.set_state("Function")
        if token.get_value() == "(":
          small_brace += 1
        if token.get_type() in ["Id","Quotes"]:
          dbg_msg.append_args(token.get_value())


      print "parser: ======TESTING: Token value: ",token.get_value()
      print "parser: ======TESTING: Token type: ",token.get_type()

    print "parser: ***********all tables ***********************"
    print
    print "parser: -----------Rest-------------------"
    for val in rest:
      print "parser: Function: ", val.get_function().get_func_name(), " Message: ", val.get_dbg_msg().get_message()," Debug Args: ", val.get_dbg_msg().get_args()

    print
    print "parser: ----------cmplt_msg_tbl--------------------"
    for hash_key in cmplt_msg_tbl.keys():
      val = cmplt_msg_tbl[hash_key]
      print "parser: Function: ", val.get_function().get_func_name(), " Message: ", val.get_dbg_msg().get_message()," Debug Args: ", val.get_dbg_msg().get_args()

    print
    print "parser: ----------partial_msg_tbl--------------------"
    for hash_key in partial_msg_tbl.keys():
      print hash_key
      val = partial_msg_tbl[hash_key]
      print "parser: Function: ", val.get_function().get_func_name(), " Message: ", val.get_dbg_msg().get_message()," Debug Args: ", val.get_dbg_msg().get_args()

#parse = parse("sample.c")
