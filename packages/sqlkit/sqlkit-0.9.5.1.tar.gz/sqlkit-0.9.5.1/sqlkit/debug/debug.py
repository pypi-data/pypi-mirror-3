"""
This module provides easy way to debug with print commands. This may not be
the best way to debug, many times ``pdb`` will be much more
powerfull. Nevertheless I found mysel in need of these functions...

The way to use this is

  1. in you library::

      dbg.write('text message', 'text2')

  2. in you application::

      dbg.debug(True)

write() - caller()
------------------
     
from now on, each time you use dbg.write()/dbg.show_caller() you'll see the
text you want to log only if you enabled it with dbg.debug(True)

If you want the log to happen in a gtk.TreeView window, you can specify:;

     import dbg
     dbg.debug(True, gtk=True)


Logging methods
---------------

Following recepe 198078 in the ASP Python CookBook (see in the code)
this module provides also a metaclass to trace the use of methods of a
particular class. It will be instantiated as::

   class A(object):
       __metaclass__ = dbg.LogTheMethods

for each method call a line will be logged (unless configured to be ignored)
with

    function called
    caller class
    arguments
    caller function
    line of code
    return code
    calling class
    time elapsed

IMPORTANT: since the logging occurs with metaclasses you need to import dbg and
           set debugging *before* importing the class you want to trace::

            import dbg
            dbg.debug(True, gtk=True)
            dbg.trace_class('SqlTable2')  # optional
            dbg.trace_function(exclude='cell_default_cb|cell_bool_cb')  # optional
            import sqlkit

TraceIt
-------

in case you need to understand who is changeing the value of a variable, you
can use TraceIt as::

    commit_allowed = dbg.TraceIt(True, name='commit_allowed', mode='rw')

and use it as a normal variable.  You'll get lines in your output stating
who changed the value of that variable, in the form::

     __str__/function_name:  old_value => new_value
     __get__/function_name:  value

  
"""

import sys, re
import new
# I had to hide this import inside functions otherwise import of sqlkit broke.
#from sqlkit.layout import misc  
import pango
import inspect
import time
import inspect
from  pdb import set_trace
import gobject

CLASS_INCLUDE = '^.*$'
CLASS_EXCLUDE = '^$'
FUNCTION_INCLUDE = re.compile('.*')
FUNCTION_EXCLUDE = re.compile('^$')

class FakeLogger(object):
    def add(self, *args,**kw):
        pass
    def write(self, *args, **kw):
         write(*args, **kw)
    def ret(self, iter, value):
        return value

DBGLogger = FakeLogger()
#DBGLogger = None
DBG = False

def test():
    global DBG
    print "DBG:", DBG
    
def debug(x=None, gtk=False):
    global DBGLogger
    global DBG
    
    if gtk == True:
        DBGLogger = get_gtk_logger(show=True)

    if x is True:
        DBG = 1
    if x is False:
        DBG = 0
    if isinstance(x , int):
        DBG = x

    
def write(*text, **kwargs):
    global DBG
    global DBGLogger
    if 'filter' not in kwargs:
        filter = None
    
    if 'sfilter' not in kwargs:
        sfilter = None
    
    if 'direct' not in kwargs:
        kwargs['direct'] = False

    if 'meth' not in kwargs:
        meth = caller()
    else:
        meth = kwargs['meth']
        
    if 'called_by' not in kwargs:
        called_by = ''
    else:
        called_by = kwargs['called_by']
        
    if DBG == 0:
        return
    if not text:
        ### FIXME: should go to DBGLogger...?
        print "%s (line %s) locals(): \n%s" % (caller(), caller(mode='lineno'),
                          dshow(caller(mode='loc', level=2), ret=True,
                                filter=filter, sfilter=sfilter,mute=True))
                                               
        return
    
    txt = ""
    for i in text:
        txt += " " + str(i)

    if not kwargs['direct'] and DBGLogger:
        try:
            instance=caller(mode='instance')
            Class_str = instance.nick
        except Exception, e:
            Class_str = ''
        
        DBGLogger.write(txt=txt, line=caller(mode='lineno'), meth=meth,
                        mode='write', Class=Class_str, caller=called_by)
    else:
        #print "dbg.write: QUI 2, DBGLogger:", DBGLogger, "direct:", kwargs['direct']
        print "%s (line %s): %s" % (caller(), caller(mode='lineno'), txt)
    
# def single_write(txt, called_by='', meth='', direct=False, **args):
#     """similar to write but accept just one text arg and some more args"""
#     global DBG
#     global DBGLogger
#     if 'filter' not in args:
#         filter = None
    
#     if 'sfilter' not in args:
#         sfilter = None
    
#     if DBG == 0:
#         return
#     if direct and DBGLogger:
#         DBGLogger.write(txt=txt, line=caller(mode='lineno'), meth=meth,
#                         mode='write', caller=called_by)
#     else:
#         print "%s (line %s): %s" % (caller(), caller(mode='lineno'), txt)


    
def caller(mode=None, level=2):
    """
    mode can be:
    lineno:  just return line number for the calling frame
    loc:     return the local variables as dict
    None:    return (class_name, caller_func)
    Class :   return class
    instance : return class if applicable
    """
    frame = sys._getframe(level)

    if mode == 'lineno':
        return frame.f_lineno
    
    if mode == 'loc':
        return frame.f_locals

    caller = frame.f_code.co_name
    class_name = ''


    try:
        a = frame.f_locals['self'].__class__
        class_name =  re.search("'(.*)'", str(a)).group(1) + "."

        if mode == 'Class':
            return a

        if mode == 'instance':
            return frame.f_locals['self']

    except:
        pass
    return "%s%s" % (class_name, caller)
    
def show_caller(filter=None, sfilter=None, loc=True):
    if DBG != 0:
        if loc:
            Locals = dshow(caller(mode='loc', level=3), ret=True,
                           filter=filter, sfilter=sfilter,mute=True)
        else:
            Locals = ''
            
        print "%s called from: %s (line %s) \n%s" % (
            caller(),
            caller(level=3), caller(level=3, mode='lineno'), Locals )
            
    
def dshow(diz, filter=None, sfilter=None, mute=False, ret=False, name=None):
    """print a dictionary in a friendly way
    filter:  only print keys that match 'filter'
    sfilter: only print keys that _don't_ match 'filter'
    """

    global DBG
    if DBG == 0:
        return
    txt = []
    if not mute:
        txt += [caller()]
    filtered = {}
    for k,v in diz.iteritems():
        if filter:
            if not re.search(filter, k):
                continue
        if sfilter:
            if re.search(sfilter, k):
                continue
        txt += ["    %s: %s" % (k, v)]
        filtered[k] = v
    if ret:
        return "\n".join(txt)
    else:
        try:
            iter = DBGLogger.write(meth=caller(), txt=name, mode='dict')
            for k,v in filtered.iteritems():
                DBGLogger.write(meth=k, txt=v, mode='value', parent=iter)
        except:
            print "\n".join(txt)

    
def ddir(obj, filter=None, sfilter=None, mute=False, ret=False):
    """print dir of an object in a readable fasion
    filter:  only print keys that match 'filter'
    sfilter: only print keys that _don't_ match 'filter'
    """

    global DBG
    if DBG == 0:
        return
    txt = []
    if not mute:
        txt += [caller()]
    for k in dir(obj):
        if filter:
            if not re.search(filter, k):
                continue
        if sfilter:
            if re.search(sfilter, k):
                continue
        v = getattr(obj, k)
        txt += ["    %s: %s" % (k, v)]
    if ret:
        return "\n".join(txt)
    else:
        print "\n".join(txt)

    
def warning(text):
    print text
    
def sql_debug(sql, params):
    msg = re.sub(':(?P<a>\S+)', '\'%(\g<a>)s\'', sql)
    #sd.debug("%s %s" % (DBG, params))
    print msg % params
    #write(msg % params)


indent = 0

### Trace
class TraceIt(object):
     """A data descriptor that sets and returns values
        normally and prints a message logging their access.
        Usi it in code like this::

           rowCommit = dbg.TraceIt(True, name='rowCommit', mode='rw')

     and use it as a normal variable.  You'll get lines in your output stating
     who changed the value of that variable, in the form::

     __str__/function_name:  old_value => new_value
     __get__/function_name:  value

     """

     def __init__(self, initval=None, name='var', mode='rw'):
         self.read = False
         if re.search('r', mode):
             self.read = True
             
         self.write = False
         if re.search('w', mode):
             self.write = True
             
         self.val = initval
         self.name = name

     def __get__(self, obj, objtype):

         if self.read:
             Caller = re.sub('.*\.([^\.]+$)', r'\1', caller(level=2))
             write("%s read %s" % (self.name, self.val),
                 called_by=Caller, meth='%s - r/%s' % (self.name, Caller))

         return self.val

     def __set__(self, obj, val):
         if self.write:
             Caller= re.sub('.*\.([^\.]+$)', r'\1', caller(level=2))
             write("%s: %s -> %s" % (self.name, self.val, val),
                 called_by=Caller, meth='%s - w/%s' % (self.name,Caller))
         self.val = val



### from a recepe in ASP:
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/198078
def trace_class(ok=None, ko=None):
    """set pattern for classes that should be traced by LogTheMethods
    Rememeber that this command need to be issued before importing the package that
    should be traced
    """

    global CLASS_INCLUDE
    global CLASS_EXCLUDE
    if ok:
        CLASS_INCLUDE = ok

    if ko:
        CLASS_EXCLUDE = ko
        
def trace_function(exclude=None, include='.*'):
    """set pattern for functions/methods that should not be traced"""

    global FUNCTION_EXCLUDE
    global FUNCTION_INCLUDE

    if exclude:
        FUNCTION_EXCLUDE = re.compile(exclude)

    if not include == '.*':
        FUNCTION_INCLUDE = re.compile(exclude)
    
def logmethod(methodname):
    def _method(self,*argl,**argd):
        global indent
        global DBGLogger
        global DBG
        
        #print "DBG", methodname,  argl, argd
        #parse the arguments and create a string representation
        #import pdb; pdb.set_trace()
        args = []
        for item in argl:
            args.append('%s' % str(item))
        for key,item in argd.items():
            args.append('%s=%s' % (key,str(item)))
        argstr = ','.join(args)   
        
        caller1 = caller(level=1).replace('._method','')
        caller2 = caller(level=2)
        caller_class = caller1
        caller_meth = caller2
        
        try:
            class_str = self.nick
        except:
            class_str = caller_class
        if DBG:
            iter = DBGLogger.add(Class=class_str, meth=methodname, indent=indent,
                                 caller=caller_meth, line=caller(mode='lineno'),
                                 args=args, class_obj=caller(mode='Class'))
        
        indent += 1
        # do the actual method call
        try:
            f = getattr(self,'_H_%s' % methodname)

            returnval = f(*argl,**argd)
            
            indent -= 1
        except Exception, e:
            DBGLogger.add(Class=class_str, meth=str(e.__class__), indent=indent,
                                 caller=methodname, line=caller(mode='lineno'),
                                 args=[e], class_obj=caller(mode='Class'))
            indent -= 1
            raise

        if DBG:
            ## iter is not defined if the method si not traced
            if iter:
                DBGLogger.ret(iter, str(returnval))

        return returnval
    
    return _method


class LogTheMethods(gobject.GObjectMeta):
    def __new__(cls, classname, bases, classdict):
        global DBG
        if re.search(CLASS_INCLUDE, classname):
            if not re.search(CLASS_EXCLUDE, classname):
                pass
        else:
            return type.__new__(cls,classname,bases,classdict)

        meths = {}

        meths.update(dict(classdict.items()))

        for base in bases:
            for attr in dir(base):
                # don't override the methods...
                if attr not in meths:
                    meths[attr] = getattr(base, attr)

        for attr, item in meths.items():
            if not DBG:
                continue
            if attr.startswith('_H_') or attr.startswith('__'):
                continue

            if callable(item) and FUNCTION_INCLUDE.match(attr) and  not \
                   FUNCTION_EXCLUDE.match(attr):
                if '_H_%s'%attr not in meths: # prevent infinite loop
                    classdict['_H_%s'%attr] = item    # rebind the method
                    classdict[attr] = logmethod(attr) # replace  by wrapper
                    classdict[attr].__doc__ = item.__doc__ # replace  by wrapper

        ret = type.__new__(cls, classname, bases, classdict)

        return ret

def get_gtk_logger(show=True):
    import gtk_dbg

    return gtk_dbg.ShowLogs(show=show)

def get_logger():
    global DBGLogger
    return DBGLogger

