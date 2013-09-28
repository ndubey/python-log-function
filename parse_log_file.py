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
import sys

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



if len(sys.argv) != 2:
  print 'Log Analyzer: Please specify one log filename on the command line.'
  sys.exit(1)
filename = sys.argv[1]
log_file = open(filename)
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





#file name line number H message
#tokenize based on space first entry file name second line number
#third H fourth till end is message
#seach message + file number



