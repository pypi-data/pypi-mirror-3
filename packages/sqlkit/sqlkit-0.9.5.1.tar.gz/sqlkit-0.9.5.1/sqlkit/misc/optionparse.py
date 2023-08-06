# coding: utf-8
"""\
:Author: M. Simionato
:Date: April 2004
:Title: A much simplified interface to optparse.

added description handling  Sandro Dentella by sandro@e-den.it 2008

You should use optionparse in your scripts as follows.
First, write a module level docstring containing something like this
(this is just an example):

'''usage: %prog files [options]
   -d, --delete: delete all files
   -e, --erase = ERASE: erase the given file'''
   
Then write a main program of this kind:

# sketch of a script to delete files
if __name__=='__main__':
    import optionparse
    option,args=optionparse.parse(__doc__)
    if not args and not option: optionparse.exit()
    elif option.delete: print "Delete all files"
    elif option.erase: print "Delete the given file"

Notice that ``optionparse`` parses the docstring by looking at the
characters ",", ":", "=", "\\n", so be careful in using them. If
the docstring is not correctly formatted you will get a SyntaxError
or worse, the script will not work as expected.
"""

import optparse, re, sys

USAGE = re.compile(r'\s*(?P<descr>.*)\s*\s*usage: (?P<usage>.*?)(\n[ \t]*\n|$)',
                   re.DOTALL|re.UNICODE|re.LOCALE)

def nonzero(self): # will become the nonzero method of optparse.Values       
    "True if options were given"
    for v in self.__dict__.itervalues():
        if v is not None: return True
    return False

optparse.Values.__nonzero__ = nonzero # dynamically fix optparse.Values

class ParsingError(Exception): pass

optionstring=""

def exit(msg=""):
    raise SystemExit(msg or optionstring.replace("%prog",sys.argv[0]))

def parse(docstring, arglist=None):
    global optionstring
    optionstring = docstring
    match = USAGE.search(optionstring)
    if not match:
        raise ParsingError("Cannot find the option string")
#    optlines = match.group('usage').splitlines()
    optlines = re.split('\n\s*(?=[-,])', match.group('usage'))
    try:
        descr = match.group('descr')
        p = optparse.OptionParser(optlines[0], description=descr,
                                  formatter=IndentedHelpFormatterWithNL() )
        for line in optlines[1:]:
            opt, help=line.split(':')[:2]
            short,long=opt.split(',')[:2]
            if '=' in opt:
                action='store'
                long=long.split('=')[0]
            else:
                action='store_true'

            p.add_option(str(short.strip()),str(long.strip()),
                         action = action, help = re.sub('\s+', ' ', help.strip()))
    except (IndexError,ValueError):
        raise ParsingError("Cannot parse the option string correctly")
    return p.parse_args(arglist)



class IndentedHelpFormatterWithNL(optparse.IndentedHelpFormatter):
    """
    This is part of a class that I read in message:
    # originally from Tim Chase via comp.lang.python.
    http://groups.google.com/group/comp.lang.python/browse_frm/thread/e72deee779d9989b/
    """
    def format_description(self, description):

        import textwrap

        if not description:
            return ""
        desc_width = self.width - self.current_indent
        indent = " "*self.current_indent

        bits = description.split('\n')
        formatted_bits = [textwrap.fill(bit, desc_width,
                                        initial_indent=indent,
                                        subsequent_indent=indent)
                          for bit in bits]
        
        result = "\n".join(formatted_bits) + "\n"
        return result


