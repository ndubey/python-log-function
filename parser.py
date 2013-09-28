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
from utils import global_tbl_entry, insert_in_tbl

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

def num_args(msg):
  return msg.count('%')

def pos_first_arg_occ(msg):
  return msg.find('%')


class parse:
  def __init__(self,filename):
    from lexer import lexer, token
    from parser import parser
    self.filename = filename
    entry = global_tbl_entry()
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
            insert_in_tbl(entry, dbg_msg, aFunction);
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
    for val in entry.rest_in_list:
      print "parser: Function: ", val.get_function().get_func_name(), " Message: ", val.get_dbg_msg().get_message()," Debug Args: ", val.get_dbg_msg().get_args()

    print
    print "parser: ----------cmplt_msg_tbl--------------------"
    for hash_key in entry.cmplt_msg_tbl.keys():
      val = entry.cmplt_msg_tbl[hash_key]
      print "parser: Function: ", val.get_function().get_func_name(), " Message: ", val.get_dbg_msg().get_message()," Debug Args: ", val.get_dbg_msg().get_args()

    print
    print "parser: ----------partial_msg_tbl--------------------"
    for hash_key in entry.partial_msg_tbl.keys():
      print hash_key
      val = entry.partial_msg_tbl[hash_key]
      print "parser: Function: ", val.get_function().get_func_name(), " Message: ", val.get_dbg_msg().get_message()," Debug Args: ", val.get_dbg_msg().get_args()
    return entry
#parse = parse("sample.c")
