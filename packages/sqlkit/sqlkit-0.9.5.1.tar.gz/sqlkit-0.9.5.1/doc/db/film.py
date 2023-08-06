from elixir import *

metadata.bind = "sqlite:///movies.sqlite"
#metadata.bind.echo = True

from datetime import datetime, timedelta

import time
#import sqlkit 
#from sqlkit.db import proxy
#import gtk
#db = proxy.DbProxy(engine="sqlite:///movies.sqlite")


class Director(Entity):
    last_name = Field(String(60))
    first_name = Field(String(60))
    movies = OneToMany('Movie', inverse='director')
    using_options(tablename='director')

    def __repr__(self):
        return u'<Director: %s>' %self.last_name

class Movie(Entity):
    #id = Field(Integer, primary_key=True)
    title = Field(String(60))
    description = Field(String(512))
    date_release = Field(DateTime)
    director = ManyToOne('Director', inverse='movies')
    actors = ManyToMany('Actor', inverse='movies', tablename='movie_casting')
    genres = ManyToMany('Genre', inverse='movies', tablename='movie_genre')   
    using_options(tablename='movie')

    def __repr__(self):
        return u'<Movie: %s>' % self.title

class Genre(Entity):
    name = Field(Unicode(15), primary_key=True)
    movies = ManyToMany('Movie')
    using_options(tablename='genre')
    
    def __repr__(self):
        return u'<Genre "%s">' % self.name

class Actor(Entity):
    name = Field(String(60))
    movies = ManyToMany('Movie', inverse='actors', tablename='movie_casting')
    using_options(tablename='actor')

setup_all()

# olmi = Director(last_name='Olmi', first_name='Ermanno')
# f100 = Movie(title='100 chiodi')
# re = Movie(title='La leggenda del re pescatore')
# pirati = Movie(title='Cantando dietro il paraventi')
# olmi.movies=[f100, re, pirati]
#olmi.movies.append(re)
#olmi.movies.append(pirati)


cento = Movie.get_by(title='100 chiodi')
print cento.director
#create_all()

#session.flush()
