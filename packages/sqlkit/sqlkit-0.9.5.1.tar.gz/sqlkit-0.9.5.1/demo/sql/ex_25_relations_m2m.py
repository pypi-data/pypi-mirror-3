"""relation/m2m 

To add a relation is as easy as adding the relation name to the layout
note that in this case the table name is not sufficient, we need to know
the mapping so we pass a class_ attribute that is really a class build with
declarative layer

In this case you cannot add actors from the interface, but you can select them
and add them to the cast of the film (as well as genres).

You can set actors'table editable if you like. Have a look at one of the next
examples. 


"""

lay = """
         title       year
         director_id - - -
         m2m=genres -  m2m=actors -
         """
t = SqlMask(model.Movie, dbproxy=db , layout=lay)


