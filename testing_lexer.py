"""
######################################################################
#
#   @file
#    testing_lexer.py
#   @brief
#    Testing modified lexer. Originally shelx
#
#   @detail
#    Making shelx work for c
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


if len(sys.argv) != 2:
  print 'Please specify one filename on the command line.'
  sys.exit(1)
filename = sys.argv[1]
print "Lexing on file:", filename
body = file(filename, 'rt').read()
print 'ORIGINAL:', repr(body)
print
print
print '-------------TOKENS:------------------'
lexer = lexer(body)
for token in lexer:
  print "======TESTING: Token value: ",token.get_value()
  print "======TESTING: Token type: ",token.get_type()
