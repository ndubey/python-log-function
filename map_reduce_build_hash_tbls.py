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
from threading import Thread
from parser import parse
from lexer import lexer

#open current directory
path = "."
def map_reduce(path):
  from parser import parse
  from lexer import lexer
  print path
  #for each folder in this folder spawn a thread
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
        parse = parse(file)



map_reduce(path)
if len(sys.argv) != 2:
  print 'parser: Please specify one filename on the command line.'
  sys.exit(1)
filename = sys.argv[1]

#for each .c and .cpp file in this folder do processing
