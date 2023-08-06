from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, Date, MetaData, ForeignKey, create_engine, engine
from sqlalchemy.orm import relation, scoped_session, sessionmaker


Base = declarative_base()
meta = Base.metadata
meta.bind = create_engine('sqlite://')
Session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=meta.bind))
session = Session()

class User(Base):
    __tablename__ = 'user'

    id = Column('id', Integer, primary_key=True)
    first_name = Column('first_name', String(50))
    addresses = relation("Address", backref="user")

class Address(Base):
    __tablename__ = 'address'

    id = Column('id', Integer, primary_key=True)
    email = Column('email', String(50))
    date_created = Column('date_created', Date)
    user_id = Column('user_id', Integer, ForeignKey('user.id'))
    provider_id = Column('provider_id', Integer, ForeignKey('provider.id'))

class Provider(Base):
    __tablename__ = 'provider'

    id = Column('id', Integer, primary_key=True)
    provider = Column('provider', String(50))
    country_id = Column('country_id', Integer, ForeignKey('country.id'))
    addresses = relation("Address", backref="provider")

class Country(Base):
    __tablename__ = 'country'

    id = Column('id', Integer, primary_key=True)
    country = Column('country', String(50))
    addresses = relation("Provider", backref="country")


