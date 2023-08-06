"""signals/record-selected

'record-selected' is define both fr SqlTable and SqlMask

"""


t = SqlTable(model.Director, dbproxy=db, )
t2 = SqlTable(model.Movie, dbproxy=db,  )

def show_movies(widget):
    if widget.current:
        t2.set_records(widget.current.movies)
    
t.connect('record-selected', show_movies)
          
t.reload()

