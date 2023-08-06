#!/usr/bin/python 

import sys

sys.path.insert(0, '../..')
import dbg
dbg.debug(False)
dbg.debug(True, gtk=True)
dbg.trace_class(ok='SqlTable|SqlWidget|SqlMask')
but = 'set_fkey_descr|(lookup|get)_value|[el]ne_cb|match_func' + \
       '|cell_default_cb|cell_bool_cb|lookup_value|is_fkey|instance2'
dbg.trace_function(exclude=but)

#from elixir import *
import elixir
from datetime import datetime, timedelta

import time
import sqlkit 
from sqlkit.db import proxy
from sqlkit import completion
#from sqlkit.completion import set_description_field
#import gtk

elixir.metadata.bind = "sqlite:///movies.sqlite"
#metadata = elixir.metadata
#elixir.metadata.bind.echo = True

db = proxy.DbProxy(engine="sqlite:///movies.sqlite")
__metadata__ = db.metadata
#__metadata__.bind.echo = True

#__session__ = db.get_session()
#ss = db.get_session()

# def get_session(obj):
#     from sqlalchemy.orm import sessionmaker
#     Session = sessionmaker(bind=__metadata__.bind)
#     return Session.object_session(obj)

class Director(elixir.Entity):
    last_name = elixir.Field(elixir.String(60))
    first_name = elixir.Field(elixir.String(60))
    movies = elixir.OneToMany('Movie', inverse='director', lazy="False")
#    movies = elixir.OneToMany('Movie', inverse='director', lazy="False", cascade="all, delete-orphan" )
    elixir.using_options(tablename='director')
#    elixir.using_options(session=ss)
#    elixir.using_options(metadata=elixir.metadata)

    def __repr__(self):
        return u'<Director: %s>' %self.last_name

class Movie(elixir.Entity):
    #id = Field(Integer, primary_key=True)
    title = elixir.Field(elixir.String(60))
    description = elixir.Field(elixir.String(512))
    year = elixir.Field(elixir.Integer())
    director = elixir.ManyToOne('Director', inverse='movies' , lazy="False")
#     actors = elixir.ManyToMany('Actor', inverse='movies', tablename='movie_casting')
#     genres = elixir.ManyToMany('Genre', inverse='movies', tablename='movie_genre')   
#    elixir.using_options(session=ss)
    elixir.using_options(tablename='movie')

    def __repr__(self):
        return u'<Movie: %s>' % self.title

class Genre(elixir.Entity):
    name = elixir.Field(elixir.Unicode(15), primary_key=True)
    movies = elixir.ManyToMany('Movie')
    elixir.using_options(tablename='genre')
#    elixir.using_options(session=ss)
    
    def __repr__(self):
        return u'<Genre "%s">' % self.name

class Actor(elixir.Entity):
    name = elixir.Field(elixir.String(60))
#    movies = elixir.ManyToMany('Movie', inverse='actors', tablename='movie_casting')
    elixir.using_options(tablename='actor')
#    elixir.using_options(session=ss)

elixir.setup_all()

lay = """first_name last_name
         o2m=movies      - - -
         """
tm = sqlkit.SqlMask(Director.mapper, metadata=__metadata__, session=elixir.session,layout=lay)
t = tm.mfields['movies'].widget.table


#olmi = Director.get_by(last_name='Olmi', first_name='Ermanno')
#ofilms = olmi.movies
#ofilms.pop()
#olmi.movies = ofilms
#elixir.session.commit()
#print olmi.movies
#f100 = Movie.get_by(title='100 chiodi')

#re = Movie(title='La leggenda del re pescatore')
#pirati = Movie(title='Cantando dietro il paraventi')
#olmi.movies=[f100, re, pirati]
#olmi.movies.append(re)
#olmi.movies.append(pirati)


#create_all()

#session.flush()

#t1 = sqlkit.SqlMask(Movie.mapper, metadata=metadata, session=elixir.session,)
#t1.reload()

#print lay
#tm = sqlkit.SqlMask(Director.mapper, metadata=metadata, session=elixir.session)
#tm = sqlkit.SqlTable(Director.mapper, metadata=metadata, session=elixir.session)




#td = sqlkit.SqlTable(Movie.mapper, metadata=metadata, session=elixir.session,)
#                     addto=tm.w['A=uno'], naked=True)
#tm = sqlkit.SqlTable(Movie.mapper, dbproxy=db)

#tm = sqlkit.SqlMask(Movie.mapper, metadata=metadata, session=elixir.session)


completion.set_description_fields('director', 'last_name', add='first_name',
                      format="%(first_name)s %(last_name)s")

completion.set_description_fields('director', 'last_name', add='first_name',
                      format="%(last_name)s - (%(first_name)s)")

#print f100.director
#print t1.records
#print t1.records[0].director

# for j in t1.session:
#     print j, get_session(j)
#     print j.director

#q = session.query(Movie)
#r2 = q.filter_by(director_id=1).all()

#gtk.main()
