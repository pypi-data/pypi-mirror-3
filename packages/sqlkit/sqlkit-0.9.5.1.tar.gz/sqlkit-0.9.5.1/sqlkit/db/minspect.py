import sys
import re
import datetime
import decimal

import sqlalchemy 
from  sqlalchemy.orm import properties
import sqlalchemy.types as sqltypes

from sqlkit import debug as dbg, exc
from sqlkit.misc.utils import Container
from sqlalchemy.sql import expression


SA_TYPE_MAP =  {
    sqlalchemy.types.String : str,
    sqlalchemy.types.Unicode : str,
    sqlalchemy.types.Integer  : int,
    sqlalchemy.types.SmallInteger  : int,
    sqlalchemy.types.Float  : float,
    sqlalchemy.types.DateTime  : datetime.datetime,
    sqlalchemy.types.Date  : datetime.date,
    sqlalchemy.types.Interval  : datetime.timedelta,
    sqlalchemy.types.Time  : datetime.time,
    sqlalchemy.types.Numeric : decimal.Decimal,
    sqlalchemy.types.Text  : str, 
    sqlalchemy.types.UnicodeText  : str, 
    sqlalchemy.types.Boolean  : bool, 
    sqlalchemy.types.Binary : str, # ????  TODO: this is probably useless
                                   # ???? but w/o you get errors browsing a db that uses them...
    }

try:
    SA_TYPE_MAP[sqlalchemy.types.LargeBinary] = str
except AttributeError:
    pass # sqlalchemy < 0.6

PROPERTIES = properties
class MissingPrimaryKeyError(Exception): pass

class InspectMapper(Container):
    """inspect a mapper and gather all info on fields normally used.
    Adds attributes for each field_name pointing to a dictionary with:
    
    table_name  (string)
    name        (string)
    table       (sqlalchemy Table obj)
    db_type     (db type)
    type        (python-type) 
    col_spec    (string) eg: INTEGER, STRING
    length      None or a Number
    property    the property used to access these data
    """
    field_list = None  # list of field_names in the mapper (all possible tables)
    props  = None  # dict of properties 
    pkeys  = None  # dict table:[pkey1,...]

    def __init__(self, mapper, noup=None):
        """
        noup: set of fields that will get a rw=False field
        ro:   bool. if True no update/insert/delete will be possible
           """
        global SA_TYPE_MAP
        
        try:
            # FIXME: these import should be avoided!...
            import sqlalchemy.dialects.postgresql
            import sqlalchemy.databases
            SA_TYPE_MAP.update({
                sqlalchemy.databases.postgres.PGInet  : str, 
                sqlalchemy.databases.postgres.PGInterval  : datetime.timedelta, 
                sqlalchemy.dialects.postgresql.base.INTERVAL :  datetime.timedelta, 
                })
        except Exception, e:
            pass

        self.field_list = []
        self.fields = Container()
        self.primarytable = self.get_primary_table
        self.noup = noup or set()
        self.mapper = mapper
        self.props = []
        self.pkeys = {}
        self.table_mappers = {}  # mappers to tables
        self.n = 0
        self.loop_on_props()

                              
    def get_py_type(self, Type, field_name):
        for typ in (Type,) + Type.__mro__:
            try:
                return SA_TYPE_MAP[typ]
            except KeyError:
                continue

        msg = "Couldn't resolve SA type for field_name '%s' %s" % (field_name, Type)
        raise NotImplementedError(msg)
        
        
    def loop_on_props(self):
        """Add field gathering info from the mapper 
        At the mome we only use properties that are 
        """
        props = self.mapper.iterate_properties
        
        for prop in props:
            if isinstance(prop, properties.ColumnProperty):
                self._add_field(prop.key, self.mapper, property=prop)
            elif isinstance(prop, properties.PropertyLoader):
                self._add_loader_field(prop.key, self.mapper, property=prop)
                
    def _add_field(self, field_name, mapper, property=None):
        if field_name in self:
            dbg.write("%s precedentemente definito, cerchi guai..." % field_name)
            return
        
        self.field_list += [ field_name ]
        col = mapper.c[field_name] 
        
        try:
            col_spec = mapper.c[field_name].type.compile(
                dialect=mapper.local.table.metadata.bind.engine.dialect)
        except (NotImplementedError, AttributeError),e:
            col_spec = None
        d = Container({
            'name'        :  str(field_name),
            'col'         :  col ,
            'db_type'     :  type(col.type), 
            'type'        :  self.get_py_type(type(col.type), field_name),
            'col_spec'    :  col_spec,
            'property'    :  property,
            'fkey'        :  False,
            'mapper'      :  mapper,
            })
        try:
            d['length'] = col.type.length
        except:
            d['length'] = None

        if isinstance(col, (expression._Label, expression.Function)):
            d['table'] =   None
            d['table_name'] =   None
            d['default']     =  None
            d['pkey']        =  False
            d['nullable']    =  True
            d['editable']    =  False            
        else:
            d['table']       =  col.table
            d['table_name']  =  col.table.name
            d['default']     =  col.default
            d['pkey']        =  col.primary_key
            d['nullable']    =  col.nullable
            d['editable']    =  field_name not in self.noup


        if d['table'] is not None and col.table.name not in self.table_mappers:
            #dbg.write("%s %s" % (mapper.local_table.name, self.table_mappers))
            self.table_mappers[col.table.name] = (self.mapper.class_, self.mapper)
            self.pkeys[col.table.name] = []

        if d['pkey']:
            #dbg.write("si %s -> %s" % (field_name, mapper.local_table.name ))
            self.pkeys[col.table.name] += [field_name]

        d['fkey'] = mapper.c[field_name].foreign_keys

        self.fields.add_element(field_name, d)
        #setattr(self.fields, field_name,  d)

    def _add_loader_field(self, field_name, mapper, property=None):
        """
        Add db_specs for a field that correspond to a Loader of a foreign field
        This is the loader of a field in a table connected via an intermediate one or
        via a OneToMany relation

        No real attribute is present in the db table

        SqlMask will use CollectionWidget to represent it and will explicily be asked to
        via a field in the layout
        """

        if field_name in self:
            dbg.write("%s precedentemente definito, cerchi guai..." % field_name)
            return
        
        self.field_list += [ field_name ]

        d = {
            'mapper'  :  property.mapper ,
            'name'        :  str(field_name),
            'table'       :  property.target,
            'table_name'       :  property.target.name,
#            'col'         :  property.mapper.c[field_name] ,
            'db_type'     :  None,   ## FIXME: this is used tor table 
            'type'        :  str,  # FIXME
            'col_spec'    :  None,
#            'is_serial'   :  False,
            'property'    :  property,
            'fkey'        :  False,
            'default'     :  None,
            'pkey'        :  None,
            'nullable'    :  True,
#            'mapper'      :  mapper,
            'editable'        :  True,
#            'direction'   :  mapper.props[field_name].direction
#            'remote_attr' : [c.name for c in property.remote_side]
            }

        try:
            d['length'] = mapper.c[field_name].type.length
        except:
            d['length'] = None


        table_name = getattr(mapper.local_table, 'name', None)
        if table_name and table_name not in self.table_mappers:
            self.table_mappers[table_name] = (mapper.class_, mapper)
            self.pkeys[table_name] = []

        self.fields.add_element(field_name, d)
        #setattr(self.fields, field_name,  d)

    def keys(self):
        """Return all the field_names in the mapper but not loaders
        """
        ret = []
        for m in self._tables(mode='mapper' ):
            ret += m.c.keys()
        return ret

    def all_keys(self):
        """Return all the field_names in the mapper comprising loaders
        """
        ret = []
        for prop in self.mapper.iterate_properties:
            ret += [prop.key]
        return ret

    def __iter__(self):
        return self

    def __contains__(self, item):
        if item in self.field_list:
            return True
        return False

    def __getitem__(self, item):
        #print "item", item, type(item)
        return getattr(self, str(item))
    
    def __len__(self):
        return len(self.field_list)
    
    def _tables(self, mode='name'):
        """return the table_names of the tables in the mapper
        if mode='mapper', returns the mappers
        the main table will be in position '0'
        """
        #dbg.write(self.table_mappers)
        if mode == 'name':
            first_table = self.mapper.local_table.name 
            ret = [t for t in self.table_mappers.keys() if t != first_table ]
            return [ first_table ] + ret
            #dbg.write(self.table_mappers.keys())
            #return self.table_mappers.keys()
        else:
            first_mapper = self.mapper
            ret = [t[1] for t in self.table_mappers.values()
                   if t[1] != first_mapper]
            #dbg.write([t[1] for t in self.table_mappers.values()])
            return [ first_mapper ] + ret
            
    def table_fields(self, table_name):
        """list of all field_names in 'table' """
        return [f for f in self.field_list if self[f]['table_name'] == table_name ]
    
    def prop_fields(self, table_name):
        """list of all field_names in 'table' linked as propperty prop"""
        table_name = [p[2] for p in self.props if p[0] == table_name][0]
        return self.table_fields(table_name)
    
    def get_mapper(self, table_name):
        """return the mapper of that table"""
        dbg.write('table_mappers', self.table_mappers)
        return self.table_mappers[table_name][1]
    
#     def mapper(self, table_name):
#         """return the mapper of that table"""
#         return self.table_mappers[table_name][1]
    
    def get_class(self, table_name):
        """return the class of that table"""
        return self.table_mappers[table_name][0]
    
    def get_pkeys(self, table_name):
        """return the list of the pkeys for that table"""
        try:
            return self.pkeys[table_name]
        except KeyError:
            raise MissingPrimaryKeyError("%s does not seem to have a PKey" %
                                         table_name)
        
    def get_join_cnd(self):
        tables = self._tables(mode='mapper')
        return get_join_cnd(tables)

    def get_primary_table(self, name=True):
        primarytable = self.mapper.local_table
        while isinstance(primarytable, sqlalchemy.sql.Join):
            primarytable = primarytable.left
        if name:
            return primarytable.name
        else:
            return primarytable

    def next(self):
        """returns the next item in the data set,
        or tells Python to stop"""
        if self.n is None:
            self.n = -1
          
        try:
            self.n += 1
            r = getattr(self, self.field_list[self.n])
        except:
            raise StopIteration
      
        if not r:
            raise StopIteration
        return r

    def is_fkey(self, field_name):
        """
        return True if this field is a foreign key
        """
        return bool(self.fields[field_name]['fkey'])

    def is_primary(self, field_name):
        """
        return True if this field is a Primary Key
        """
        return bool(self.fields[field_name]['pkey'])

    def is_loader(self, field_name):
        """
        True if field_name is a loader for a related table
        """
        if field_name not in self.field_list:
            return False

        prop = self.fields[field_name]['property']
        if isinstance(prop, properties.PropertyLoader):
            return True
        return False

    def is_string(self, field_name):
        """
        Return true if this field is a String type
        """
        db_type = self.fields[field_name]['db_type']
        if db_type:
            return issubclass(db_type, (sqltypes.String))
        return False

    def is_date(self, field_name):
        """
        Return true if this field is  date
        """
        db_type = self.fields[field_name]['db_type']
        if db_type:
            return issubclass(db_type, (sqltypes.Date))
        return False

    def is_datetime(self, field_name):
        """
        Return true if this field is  datetime
        """
        db_type = self.fields[field_name]['db_type']
        if db_type:
            return issubclass(db_type, (sqltypes.DateTime))
        return False

    def is_time(self, field_name):
        """
        Return true if this field is time
        """
        db_type = self.fields[field_name]['db_type']
        if db_type:
            return issubclass(db_type, (sqltypes.Time))
        return False

    def is_interval(self, field_name):
        """
        Return true if this field is time
        """
        db_type = self.fields[field_name]['db_type']
        if db_type:
            if issubclass(db_type, (sqltypes.Interval)):
                return True
            elif self.fields[field_name]['type'] is datetime.timedelta:
                return True
        return False

    def is_integer(self, field_name):
        """
        Return true if this field is integer
        """
        db_type = self.fields[field_name]['db_type']
        if db_type:
            return issubclass(db_type, (sqltypes.Integer))
        return False

    def is_float(self, field_name):
        """
        Return true if this field is float
        """
        db_type = self.fields[field_name]['db_type']
        if db_type:
            return issubclass(db_type, (sqltypes.Float))
        return False

    def is_numeric(self, field_name):
        """
        Return true if this field is numeric
        """
        db_type = self.fields[field_name]['db_type']
        if db_type:
            return issubclass(db_type, (sqltypes.Numeric))
        return False

    def is_number(self, field_name):
        """
        Return true if this field is a number
        """
        db_type = self.fields[field_name]['db_type']
        if db_type:
            return issubclass(db_type, (sqltypes.Numeric, sqltypes.Integer, sqltypes.Float))
        return False

    def is_boolean(self, field_name):
        """
        Return true if this field is  date
        """
        db_type = self.fields[field_name]['db_type']
        if db_type:
            return issubclass(db_type, sqltypes.Boolean)
        else:
            return False

    def is_text(self, field_name):
        """
        Return true if this field is  date
        """
        db_type = self.fields[field_name]['db_type']
        if db_type:
            return issubclass(db_type, (sqltypes.Text))
        return False

    def is_enum(self, field_name):
        """
        Return true if this field is  date
        """
        from sqlkit import fields

        col = self.fields[field_name]['col']
        try:
            field = col.info.get('field', None)
            if field:
                return issubclass(field, fields.EnumField)
            return col.info.get('render') == 'enum'
        except AttributeError:
            pass

    def is_image(self, field_name):
        """
        Return true if this field is  date
        """
        from sqlkit import fields

        col = self.fields[field_name]['col']
        try:
            field = col.info.get('field', None)
            if field:
                return issubclass(field, fields.ImageField)
            return col.info.get('render') == 'image'
        except AttributeError:
            pass

    def is_file(self, field_name):
        """
        Return true if this field is  date
        """
        from sqlkit import fields

        col = self.fields[field_name]['col']
        try:
            field = col.info.get('field', None)
            if field:
                return issubclass(field, fields.FileField)
            return col.info.get('render') == 'filename'
        except AttributeError:
            pass

    def is_nullable(self, field_name):
        """
        Return true if this field is  date
        """
        return self.fields[field_name]['nullable']

    def __str__(self):
        return "InspectMapper for keys: %s" % self.keys()
        
    def __repr__(self):
        return "<InspectMapper for keys: %s>" % self.keys()

def get_foreign_info(ForeignKey, names=True):
    """
    return a tuple (fk_table, fk_column)
    :param names: return names instead of objects
    """
    foreign_keys = ForeignKey

    if len(foreign_keys) > 1:
        raise exc.UnhandledMultipleForeignKeys(foreign_keys)
    else:
        fkcol = foreign_keys.copy().pop()  # since 0.7 it's a set, no indexing
        ## table/column name are unicode but they must be string to be
        ##     used as key in dicts
        if names:
            return (str(fkcol.column.table.name), str(fkcol.column.name))
        else:
            return (fkcol.column.table, fkcol.column)
    



def get_props_for_delete_orphan(mapper, field_name):
    """
    discover if field_name setting needs to set an object to fullfill the request
    for a delete_orphan cascading on a possible relation
    returns the generator for the properties or ()
    """
    ## TODO: FIX this. this is not working correctly tests must be added

    ## eg. Movies.__mapper__, director_id
    # when setting director_id you neeed to set also director so that
    # the backref relation from Director to Movie (that has delete_orphan set)
    # will not complain that Movie has no parent

    # find out if director_id is implied in some relation (director for us)
    # look in local_remote_pairs

    prop = mapper.get_property(field_name)
    assert isinstance(prop, properties.ColumnProperty)
    assert len(prop.columns) == 1  # I don't handle mapper with two columns in a property
    column = prop.columns[0]

    if hasattr(column, 'info'):

        if sqlalchemy.__version__ >= '0.6' or column.info.get('attach_instance'):

            prop_names = column.info.get('attach_instance')
            if isinstance(prop_names, basestring):
                prop_names = (prop_names,)

            if not prop_names:
                return ()
            return [mapper.get_property(prop_name) for prop_name in prop_names
                    if mapper.has_property(prop_name)]

        else:
            props = []
            for pr in mapper.iterate_properties:
                if isinstance(pr, properties.RelationProperty):
                    if pr.direction.name in ('MANYTOONE',):
                        for col in pr.local_remote_pairs[0]:
                            # I can't use col in p.local_remote_pairs
                            # as it uses 'col == p.local_remote_pairs' that evaluates
                            # to a BinaryExpression
                            if column is col:
                                try:
                                    if pr.backref.prop.cascade.delete_orphan:
                                        props += [pr]
                                except AttributeError, e:
                                    pass
            return tuple(props)

