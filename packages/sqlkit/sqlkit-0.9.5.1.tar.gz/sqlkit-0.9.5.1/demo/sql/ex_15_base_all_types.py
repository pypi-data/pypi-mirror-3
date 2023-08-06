"""base/all types

simple mask showing all supported types. Some are clearly poorely rendered.


"""

lay = """
{|.text  varchar10   varchar200
         text        - -
         uni
         uni_text    - -
         }

{|.date
         date        time
#         datetime    datetime_tz
         datetime    
         time_tz     interval
         }

{|.numbers
         integer
         float        numeric
         }
{|.boolean
         bool         bool_null
         }
         
"""

t = SqlMask(model.AllTypes, layout=lay, dbproxy=db )
for name in ('text','date', 'numbers', 'boolean'):
    t.set_frame_label(name, name)
t.reload()


t1 = SqlTable(model.AllTypes, dbproxy=db )
t1.reload()



