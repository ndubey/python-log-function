"""
######################################################################
#
#   @file
#    map_build_hash_tbls.py
#   @brief
#    For each folder starting from parent spawn a thread to hadle all .c
#    or .cpp file. This spawned thread will read each of the listed file
#    for each file it will call make_log_msg_func_tbl to create the three
#    tables.
#
#   @detail
#    List all folder in current directory spawn a similar thread to handle that
#    directory. Do the current folder processing here in this thread. List all
#    .c and .cpp files and for each file call make_log_msg_func_tbl. After it
#    finishes combine in single set of three file.
#    Now join with all spawned thread one by one and on finish append the subfolder
#    file in parent.
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
import os, sys
import re
import threading
from parser import parse
from lexer import lexer
from utils import debug_msg, function, value, global_tbl_entry
from threading import Thread

class global_tbl:
  def __init__(self):
    self.lock = threading.Lock()
    self.tbl = []

#open current directory
path = "."
def map_reduce(path):
  from parser import parse
  from lexer import lexer
  from utils import function, debug_msg, insert_in_tbl
  #build hash table from file or scanning the complete source file
  #check for input args
  #global the_tbl
  the_tbl = global_tbl()
  if os.path.isfile(path) and path.endswith(".tbl"):
    #read file to create the_tbl
    f = open(path)
    entry = None
    func = None
    for line in f:
      if line.startswith("&#?filename:"):
        #acquire the global_etntry_tbl lock and add this entry
        #for this file
        if entry:
          the_tbl.lock.qcquire()
          the_tbl.tbl.append(entry)
          the_tbl.lock.release()
        
        filename_start = line.find(':')
        file_name = line[filename_start+1:]
        print "File name is: ", file_name
        entry = global_tbl_entry()
        entry.set_file_name(file_name)
      elif line.startswith("\t&#?func_name:"):
        #	&#?func_name:func&#?func_args:int a&#?macro_name:MSG&#?message:I am Nandan&#?msg_args:
        func = function()
        function_name_start = line.find(':')
        function_name_end = line.index("&#?func_args:")
        func_name = line[function_name_start+1:function_name_end]
        print "Func name: ", func_name
        function_args_start = function_name_end + 13
        func_args_end = line.index("&#?macro_name:")
        func_args = line[function_args_start+1:func_args_end]
        func.set_name(func_name)
        func.set_args(func_args)
        print "Func args: ", func_args
        #message
        dbg_msg = debug_msg()
        dbg_macro_start = line.find("&#?macro_name:") + 14
        dbg_msg_macro_end = line.index("&#?message:")
        macro_name = line[dbg_macro_start:dbg_msg_macro_end]
        print "Macro name: ", macro_name
        dbg_msg.set_macro_name(macro_name)
        dbg_msg_start = dbg_msg_macro_end + 11
        dbg_msg_end = line.index("&#?msg_args:")
        msg = line[dbg_msg_start:dbg_msg_end]
        print "message: ", msg
        dbg_msg.set_message(msg)
        dbg_msg_args_start = dbg_msg_end + 12
        args = line[dbg_msg_args_start:]
        dbg_msg.set_args(args)
        print "msg args: ", args
        insert_in_tbl(entry,dbg_msg, func)
    #insert the last entry
    if entry:
      the_tbl.lock.acquire()
      the_tbl.tbl.append(entry)
      the_tbl.lock.release()

    return the_tbl
  #else scan/parse directory to make the_tbl

  print path
  #create table write table
  the_tbl = make_tbl(path)
  save_tbl_in_file(the_tbl.tbl)
  return the_tbl
def save_tbl_in_file(tbl):
  #create a new file linux_data_logs.tbl
  f = open("linux_data_logs.tbl", 'w')
  for entry in tbl:
    #write file_name
    f.write("&#?filename:")
    f.write(entry.file_name)
    f.write("\n")
    write_cmplt_msg_tbl(f,entry.cmplt_msg_tbl)
    write_partial_msg_tbl(f,entry.partial_msg_tbl)
    write_rest_in_list_tbl(f,entry.rest_in_list)
def write_cmplt_msg_tbl(f,cmplt_msg_tbl):
  for hash_key in cmplt_msg_tbl.keys():
    write_value(f,cmplt_msg_tbl[hash_key])
def write_partial_msg_tbl(f,partial_msg_tbl):
  for hash_key in partial_msg_tbl:
    write_value_list(f,partial_msg_tbl[hash_key])

def write_rest_in_list_tbl(f,rest_in_list):
  for value in rest_in_list:
    write_value(f,value)
def write_value_list(f,value):
  if value:
    write_value(f,value)
    write_value_list(f,value.get_next())
def write_value(f,value):
    function = value.get_function()
    dbg_msg = value.get_dbg_msg()
    f.write("\t&#?func_name:")
    f.write(function.get_func_name())
    f.write("\t&#?func_args:")
    f.write(function.get_args())
    f.write("\t&#?macro_name:")
    f.write(dbg_msg.get_macro_name())
    f.write("\t&#?message:")
    f.write(dbg_msg.get_message())
    f.write("\t&#?msg_args:")
    f.write(dbg_msg.get_args())
    f.write("\n")
def make_tbl(path):
  #for each folder in this folder spawn a thread
  the_tbl = global_tbl()
  dirs = os.listdir(path)
  print "directories and files: "
  for file in dirs:
    if os.path.isdir(file):
      print file
      thread = Thread(target = map_reduce, args = (file, ))
      thread.start()
      thread.join()
    else:
      fileExt = os.path.splitext(file)[-1]
      if fileExt in ['.c','.cpp']:
        print file
        parser = parse(file)
        entry = parser.parse_file()
        entry.set_file_name(file)
        #acquire the global_etntry_tbl lock and add this entry
        #for this file
        the_tbl.lock.acquire()
        the_tbl.tbl.append(entry)
        the_tbl.lock.release()
  return the_tbl


if len(sys.argv) != 2:
  print 'parser: Please specify one filename on the command line.'
  sys.exit(1)
path = sys.argv[1]
map_reduce(path)

#for each .c and .cpp file in this folder do processing
