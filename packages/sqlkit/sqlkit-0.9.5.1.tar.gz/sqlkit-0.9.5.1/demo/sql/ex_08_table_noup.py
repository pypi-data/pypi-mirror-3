"""base/options: noup 

year and description will not be editable (but they can be changed
programmatically)


"""

t = SqlTable('movie',
             dbproxy=db,
             order_by='director_id',
             noup='year, description',
         )
t.noup = '+director_id' # alternative way

t.reload()

