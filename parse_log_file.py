"""
######################################################################
#
#   @file
#    parse_log_file.py
#   @brief
#    This takes a log file as an argument and read the database from existing
#    prespecified file. It reads the log messages line by line and prints the
#    corresponding file/function it maps to.
#
#   @detail
#    for each log message either a file/function is printed or the message itself
#    is printed
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

#open the log file

#read line by line

#date starts with 2012 or 2013 ignore this line
import sys, os
from utils import global_tbl_entry, insert_in_tbl
from map_reduce_build_hash_tbls import map_reduce

class logMsg:
  def __init__(self):
    self.msg = None
    self.file_name = None
    self.func_name = None
    self.func_args = None
  def get_func_name(self):
    return self.func_name
  def get_msg(self):
    return self.msg
  def get_file_name(self):
    return self.file_name
  def get_func_args(self):
    return self.func_args
  def set_func_name(self,func_name):
    self.func_name = func_name
  def set_msg(self,msg):
    self.msg = msg
  def set_file_name(self,file_name):
    self.file_name = file_name
  def set_func(self,func_args):
    self.func_args = func_args


#tokenize based on space first entry file name second line number
#third H fourth till end is message
#seach message + file number
num_args = len(sys.argv)
print num_args
if num_args < 2:
  print 'Log Analyzer: Please specify one log filename on the command line.'
  print 'parser: Please specify one filename(log file in text) to parse on the command line.'
  print "Usage: python parse_log_file.py <log_file_name.txt> <optional:function_log_table_file.tbl>"
  print "If second argument is not provided first .tbl file is used"
  sys.exit(1)
log_file_name = sys.argv[1]
path = None
if num_args == 3:
  path = sys.argv[2]
if not path:
  print "Warning: No function message table file specified"
  dirs = os.listdir(".")
  for f in dirs:
    if f.endswith(".tbl"):
      path = f
      break
  if not path:
    print "Error: No function message table file found in current directory"
    print "Run map_reduce_build_hash_tbls.py file specifying the source code directory"
    print "Copy the above generated file .tbl file here "
    sys.exit(1)
print "Log file to analyze: ", log_file_name
print "log - function table file name: ", path
the_tbl = map_reduce(path)
log_file = open(log_file_name)
out_file = open(log_file_name+"function_list.txt", 'w')
for line in log_file:
  if line.startswith("2013") or line.startswith("2012"):
    pass
  else:
    if ".c" in line or ".cpp" in line:
      tokens = line.split()
      tokens
      file_name = tokens[0]
      line_num = tokens[1]
      h = tokens[2]
      index = line.find(h)
      print index
      print line[index+2:]
      #h in tokens
      msg = " ".join(tokens[3:])
      log_msg = logMsg()
      log_msg.set_file_name(file_name)
      #log_msg.set_func_name(file_name)
      log_msg.set_msg(msg)
      print "log file parsing: filename: ", file_name
      print "log file parsing: line number: ", line_num
      print "log file parsing: Debug message: ", msg
      if file_name in the_tbl.keys():
        print "This file is parsed and has saved "
        entry = the_tbl[file_name]
        print "Searching function for message: ", msg
        function_name = entry.get_func_name_from_message(msg)
        if function_name:
          print "Found function: ", function_name
          out_file.write(function_name+"\n")



#file name line number H message

