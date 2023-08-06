"""base/join

You can edit the join of 2 tables just using tables='table1 table2'

note that in a join you need to filter/add constraint on a name that is
a composition between table and field_name

"""

t = SqlTable("movie director", dbproxy=db )
t.add_filter(director_nation='IT') # NOTE director_nation
t.reload()

