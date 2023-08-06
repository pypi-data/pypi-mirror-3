"""
Babel support. If babel is not present print an explanation.
If default locale is 'C', set locale to 'en'

"""
try:
    import babel
except ImportError, e:
    print "\nSqlkit now depends on babel to provide localization. Quitting\n"
    raise e

if babel.default_locale('LC_NUMERIC') in ('c', 'C', '', None):
    import os
    os.environ['LANG'] = 'en_US'
    os.environ['LC_NUMERIC'] = 'en_US'
    reload(babel)

if babel.default_locale('LC_TIME') in ('c', 'C', '', None):
    import os
    os.environ['LC_TIME'] = 'en_US'
    reload(babel)

from babel import numbers, dates

