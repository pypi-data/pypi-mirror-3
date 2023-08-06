# DISCLAIMER: this file is not mantained. I don't use elixir

import elixir
from sqlkit.db import proxy

from model import engine

db = proxy.DbProxy(engine=engine)
__metadata__ = db.metadata
#__session__ = db.get_session()

class Director(elixir.Entity):
    last_name = elixir.Field(elixir.String(60))
    first_name = elixir.Field(elixir.String(60))
    nation = elixir.Field(elixir.String(6))
    
    movies = elixir.OneToMany('Movie', inverse='director')
    elixir.using_options(tablename='director')
    elixir.using_options(metadata=__metadata__)

    def __repr__(self):
        return u'<Director: %s (%s)>' % (self.last_name, self.nation)

class Movie(elixir.Entity):
    title = elixir.Field(elixir.String(60))
    description = elixir.Field(elixir.String(512))
    year = elixir.Field(elixir.Integer())
    date_release = elixir.Field(elixir.Date())
    director = elixir.ManyToOne('Director', inverse='movies')
    actors = elixir.ManyToMany('Actor', inverse='movies', tablename='movie_casting')
    genres = elixir.ManyToMany('Genre', inverse='movies', tablename='movie_genre')   
    elixir.using_options(tablename='movie')

    def __repr__(self):
        return u'<Movie: %s>' % self.title

class Genre(elixir.Entity):
    name = elixir.Field(elixir.Unicode(15), primary_key=True)
    movies = elixir.ManyToMany('Movie')
    elixir.using_options(tablename='genre')
    
    def __repr__(self):
        return u'<Genre "%s">' % self.name

class Actor(elixir.Entity):
    name = elixir.Field(elixir.String(60))
    movies = elixir.ManyToMany('Movie', inverse='actors', tablename='movie_casting')
    elixir.using_options(tablename='actor')

elixir.setup_all()

