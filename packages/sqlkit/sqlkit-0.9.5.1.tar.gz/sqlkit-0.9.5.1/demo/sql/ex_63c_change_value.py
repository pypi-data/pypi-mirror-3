"""hooks/on_change_value

On change value works differently according to the type of the widget.
varchar/integer field will invoke it for each typed char
enum/foreign key fields invoke it when the item is choosen
table's widget invoke it when editing is terminated

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

class Hooks(object):

    def on_change_value__text(self, sqlwidget, field_name, value, fkvalue, field):
        print "Changed: ", sqlwidget, field_name, value, fkvalue

    on_change_value__varchar10 = \
    on_change_value__date = \
    on_change_value__time = \
    on_change_value__datetime = \
    on_change_value__integer = \
    on_change_value__float = \
    on_change_value__numeric = \
    on_change_value__bool = \
    on_change_value__bool_null = on_change_value__text

t = SqlMask(model.AllTypes, layout=lay, dbproxy=db, hooks=Hooks() )

for name in ('text','date', 'numbers', 'boolean'):
    t.set_frame_label(name, name)
t.reload()


t1 = SqlTable(model.AllTypes, dbproxy=db, hooks=Hooks() )
t1.reload()
