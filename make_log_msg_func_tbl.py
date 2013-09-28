"""
######################################################################
#
#   @file
#    make_log_msg_func_tbl.py
#   @brief
#    Construct hash tables with log messages as key and function name as value
#
#   @detail
#    We will create 3 kind of hash table:
#    Log message with no argument: Directly hashed with func name and file name
#    Log message with first 3 words without argument: hashed with first
#              consecutive 3 words for this case value will be complete
#              log message, file name and func name
#    Log message which has arguments in very begning: Need to search linearly
#
#    This file also load these hash tables from existing saved structure file
#
#    Use option to rebuild with path specified to one source file else
#    existing database will be created from existing 3 files
#
#    When creating for the first time a global structure with LOGGING Macros
#         is used. There are two king of LOGGING macros
#                  1. Just MACRO e.g. LOG_FUNC_ENTRY
#                  2. LOG_MSG_HIGH("hjjj %f ",kk)
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

#get next function name

#get next token -> if id check/change state
#    ->if ( keep track of all ()
#    ->if )
#    ->if {
#    ->if }
#    if not change back the state else output saved id

#call get log messages for this function until matching } so keep track of all {}

#get log messages from this function one by one hash in one of the three
#tables
