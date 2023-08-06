"""
Simple relative date algebra
=============================

a function that implements simple relative date algebra so that we can use it
in bookmarks and queries.

Differently from what other packages do (as the very usefull relativedelta that
is used in this module) datetools tries to use the term month as a period of length
that depends on the 'current' month.  End of february + 1month will be end of march,
not 28th of march!

Allowed chars are::

  [-+ diwWmMyY @>]

letters refer to a moment of time (start/end of month, year, week) or period
according to use: the forst token is a moment of time, the further ones are
periods.

  :d: today
  :i: yesterday ('ieri' in italian, 'y' was already used by year)

  :w: beginning of week
  :W: end of week

  :m: beginning of month
  :M: end of month

  :y: beginning of year
  :Y: end of year

Math signs ``+`` and ``-`` work as you would expect they add and subtract
period of time. When used this way the following letter refers to a period::

  m+14d

is the 15th day of the month (beginning of month + 14 days)

.. versionadded:: 0.8.6.1

If the first token is the end of the month, we try to stick to the end as much as
possible, till another period is used, so that order is significant, note what follows that
is extracted from the doctests, assuming the current day is June 2th::

  >>> dt.string2date('M-1m-2d')
  datetime.date(2007, 5, 29)

  >>> dt.string2date('M-2d-1m')
  datetime.date(2007, 5, 28)


You can also use a short form (compatible with previous syntax)::

  m-1 == m-1m

You can use also > in which case the string is considered 2 dates, each built
as already stated::

  m-1 > M+2

means a 3 months period, starting from beginnig of last month to end of next
month

Periods
-------------------
@ is a compact way to set a period::

  @m == m > M
  @m-1  == m-1 > M-1

.. versionadded:: 0.8.6.1

@ accepts also a quantity::

  @2m-1 = m-1 > M-1 +1m

that means a period of 2 months starting from beginning of last month.

Other examples
--------------

  :m-1: beginnning of last month
  :M+1: end of next month

"""

import re
from dateutil.relativedelta import relativedelta
from datetime import date, timedelta
from babel import dates 
from sqlkit import _

class WrongRelativeDateFormat(Exception): pass

DATE_PATTERN = re.compile("""
    (?P<double>@)?
    (?P<math>[+-][0-9]*)?
    (?P<period>[imMdDyYwW])?
    (?P<math2>[+-][0-9]*)?
    $""",    re.VERBOSE)
CHARS = re.compile('[-+dimMwWyY>]')
TEST = False
TODAY = date.today()

def today():
    ## in tests wee need to force computation on a different day
    if TEST == True:
        return TODAY
    else:
        return date.today()
    
def string2dates(string):
    """
    return a tuple of date values (start, end) that translates 'string'
    end may be None if 'string' does not imply a period.
    
    Firstly a babel.dated.parse_date is attempted, if it fails
    math as described in the doctring of the module is applied

    Since a string definition can split into two dates, a tuple is return
    anyhow, a tipical way to call it is::

      start, end = string2dates('whatever')

    if you are sure one date is in the definition, you can use
    string2date instead 
    """
    try:
        # first try a normal parsing via babel
        return dates.parse_date(string, locale=dates.default_locale()), None
    except:
        pass
    
#     m = re.search(CHARS, string)
#     if not m:
#         return string, None

    if '@' in string:
        m = re.match('@(\d?)(([ymdw]).*)', string)
        n, base, period  = m.groups()
        string = "%s > %s" % (base.lower(), base.upper())
        if n:
            string += " +%s%s" % (int(n)-1, period)

    data = string.strip().split('>')

    if len(data) == 1:
        return (string2date(data[0]), None)
    else:
        if not data[1]:
            raise WrongRelativeDateFormat(_('Incomplete date format'))

        return ( string2date(data[0]), string2date(data[1] or None))
        
def string2date(string):
    """
    return a date represented by a string applying math syntax as described
    in the docstring

    """
    try:
        # first try a normal parsing via babel
        return dates.parse_date(string, locale=dates.default_locale())
    except:
        pass

    ## add spaces to math simbols, not in starting position, only if not
    ## preceded by spaces
    PAT_ADD_SPACES = '(?<=[^ ])([-+])'
    data = re.split(' +', re.sub(PAT_ADD_SPACES, r' \1', string).strip())
    ##
    end_month = 'M' in data[0]
    
    try:
        computed, last_period = transform(data[0])

        for token in data[1:]:
            computed, last_period = transform(token, start=computed,
                                              last_period=last_period, further=True)
            
            ## I want to stick to end of month as much as possible: if we're in june, 2nd
            #  M-1m must return end of may: 31 NOT 30!!!
            if end_month:
                if last_period == 'm':
                    computed = get_end_of_month(computed)
                elif last_period in 'dw':
                    end_month = False

    except Exception, e:
        raise WrongRelativeDateFormat(str(e))
    
    return computed
    

def transform(token, start=None, last_period=None, further=False):
    """transform token into a date
    Token is the very simple information: m +1m 2d
    if last_period is not none, the period can be missing and 'last_period'
    is used.   This allows to write: m-1 meaning 'beginning of last month'
    """
    if not start:
        start = today()

    m = re.match(DATE_PATTERN, token)

    if not m:
        raise WrongRelativeDateFormat(
            "Wrong Relative date format: %s" % token)
    else:
        period = m.group('period')

    if not period and last_period:
        period = last_period
        
    last_period = period.lower()
    

    if m.group('math'):
        math = m.group('math')
    else:
        math = m.group('math2')
    
    if math == '-':
        math = -1
    try:
        math = int(math)
    except TypeError:
        math = None
    
    if period == 'd':
        computed = start
        if math is not None:
            computed = computed + relativedelta(days=+math)

    if period == 'i':
        computed = start - timedelta(days=1)

    if period in ('w', 'W'):
        if not further:
            computed = start - timedelta(days=start.isoweekday()-1)
        else:
            computed = start
        if math is not None:
            computed = computed + relativedelta(weeks=+math)
        if period == 'W':
            computed = computed + relativedelta(weeks=+1, days=-1)
            

    if period in ('m', 'M'):
        if not further:
            computed =  start.replace(day=1)
        else:
            computed = start
        if math is not None:
            computed = computed + relativedelta(months=+math)

        if period == 'M':
            computed = computed + relativedelta(months=+1, days=-1)
            
    if period in ('y', 'Y'):
        j = int(start.strftime('%j'))
        if not further:
            computed = start - timedelta(days=j-1)
        else:
            computed = start
        if math is not None:
            computed = computed + relativedelta(years=+math)
        if period == 'Y':
            computed = computed + relativedelta(years=+1, days=-1)
            

    return (computed, last_period)

def get_end_of_month(date):
    date = date.replace(day=1)
    return date + relativedelta(months=+1, days=-1)
