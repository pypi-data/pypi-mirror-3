# This code is released into public domain.
# 
# anatoly techtonik <techtonik@gmail.com>
#

import datetime
import inspect
import os
import sys

oldfunc = None  #: save old trace function if any
def start():
    global oldfunc
    oldfunc = sys.gettrace()
    print datetime.datetime.now().strftime('TRACE START [%Y-%m-%d %H:%M:%S]')
    sys.settrace(function_trace_xdebug)
def stop():
    global oldfunc
    print datetime.datetime.now().strftime('TRACE END   [%Y-%m-%d %H:%M:%S]')
    sys.settrace(oldfunc)

trace_cwd = os.getcwd()  #: current directory is stripped from filenames
trace_depth = 0
trace_filter = ['/usr/lib/python']
# [ ] check what will happen with depth when trace started deep inside and
#     moved out (also check for Xdebug)
def function_trace_xdebug(frame, event, arg):
    '''print function trace in default xdebug human-readable format 
       http://xdebug.org/docs/execution_trace'''
    global trace_depth
    if event == 'call': # generated before any function call
        def strip_cwd(filename):
            global trace_cwd
            if trace_cwd and filename.startswith(trace_cwd):
                return os.path.normpath(filename.replace(trace_cwd, '.', 1))
            return filename
            
        trace_depth += 1
        funcname = frame.f_code.co_name
        filename = strip_cwd(frame.f_code.co_filename)
        lineno = frame.f_lineno
        param = ''
        if funcname == '<module>':
            module = inspect.getmodule(frame.f_code)
            if module:
                funcname = '<%s>' % module.__name__
            else: # inspect.getmodule() seem to fail on __import__(...) stmts
                funcname = '<>'
            # by analogy with PHP require() trace in Xdebug, the format is
            # <mod.name>(module_location) file_imported_from:line
            param = filename
            filename = strip_cwd(frame.f_back.f_code.co_filename)
        # skip paths mentioned in trace_filter
        if (funcname[0] is not '<' # not module import
                and any( [filename.startswith(x) for x in trace_filter] )):
            pass
        else:
            print '%*s-> %s(%s) %s:%s' % (trace_depth*2, '', funcname, param,
                                      filename, lineno)
        return function_trace_xdebug
    elif event == 'return':
        trace_depth -= 1
    else:
        pass #print 'TRACE: UNKNOWN %s EVENT WITH ARG %s' % (event, arg)
        return

