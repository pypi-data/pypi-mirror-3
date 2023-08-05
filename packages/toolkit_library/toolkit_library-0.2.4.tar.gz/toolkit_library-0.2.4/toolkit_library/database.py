# coding=utf-8
"""
    toolkit_library.database
    ~~~~~~~~~~~~~~~~~~~~~~~~
    Database module for manipulating databases
    Taking advantage of the famous SQL toolkit SQLAlchemy(required)
"""
import collections, inspect
from sqlalchemy.orm import scoped_session, sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy import create_engine, Column, Integer, DateTime, ForeignKey, func
from sqlalchemy.schema import Table
from types import MethodType


class Database:
    """Represent a connection to a specific database"""

    # Base is a class variable, because it has nothing to do with specific instances of this class
    # Base is used to derive user defined models, and there is a one-to-many relation between models and databases.
    Base = declarative_base() 

    class ModelBase:
        """Base model for a SQLAlchemy declarative model.
        Now provides a lower case table name and an integer primary key.
        """
        @declared_attr
        def __tablename__(cls):
            """Use lower-case class name as table name"""
            return cls.__name__.lower()

        id = Column(Integer, primary_key = True)

    def __init__(self, connection_string):
        """Initiate a database engine which is very low level,
        and a database session which deals with orm.
        """
        # Solve an issue with mysql character encoding(maybe it's a bug of MySQLdb)
        # Refer to http://plone.293351.n2.nabble.com/Troubles-with-encoding-SQLAlchemy-MySQLdb-or-mysql-configuration-pb-td4827540.html
        if 'mysql:' in connection_string and 'charset=' not in connection_string:
            raise ValueError("""No charset was specified for a mysql connection string. 
"latin1" will be used. This will cause problems sometimes.
Please specify something like '?charset=utf8' explicitly.""")

        # The engine can do everything you can do in a database command console, 
        # but it does not support orm, if you don't need orm, choose the engine.
        self.engine = create_engine(connection_string, convert_unicode = True, encoding = 'utf-8')

        # If you want to deal with orm, you need session 
        self.session = scoped_session(sessionmaker(autocommit = False, autoflush = False, bind = self.engine))
        def add_then_commit(session, obj):
            session.add(obj)
            session.commit()        
        self.session.add_then_commit = MethodType(add_then_commit, self.session)

    def create_tables(self):
        """Create all tables, make sure:
        1). All of the models extend Database.Base
        2). Import all of the models before invoking this method
        """
        Database.Base.metadata.create_all(bind = self.engine)

    def drop_tables(self):
        """Drop all tables, make sure:
        1). All of the models extend Database.Base
        2). Import all of the models before invoking this method
        """
        Database.Base.metadata.drop_all(bind = self.engine)

    def load_data(self, data):
        """Load data into database from a module or from an iterable of iterables of items.
        If the data paramter is a module, all variables ending with 's' in that module forms a new iterable,
        If the data paramter is already an iterable of iterables of items, all of the items will be added to database.
        """
        if not data:
            raise ValueError('data parameter should not be None or empty')
        if isinstance(data, collections.Iterable) and all(isinstance(items, collections.Iterable) for items in data): 
            for items in data:
                self.session.add_all(items)
            self.session.commit()
        elif inspect.ismodule(data):
            self.load_data([getattr(data, attr) for attr in dir(data) if attr.endswith('s')])
        else:
            raise TypeError('parameter data is of the wrong type')

    @staticmethod
    def foreign_key(foreign_table_name, foreign_name = None, backref_name = None):
        """"Class decorator, add a foreign key to a SQLAlchemy model.
        Parameters:
        foreign_table_name is the destination table, in a one-to-many relationship, it is the "one" side.
        foreign_name is the user-friendly name of table(if omitted, table will be used instead).
        backref_name is the name used to back ref the "many" side.
        """
        foreign_model_name = foreign_table_name.capitalize()
        foreign_name = foreign_name or foreign_table_name
        foreign_key = '{0}_id'.format(foreign_name)        
        def ref_table(cls):
            model_name = cls.__name__
            table_name = model_name.lower()
            setattr(cls, foreign_key, Column(Integer, ForeignKey('{0}.id'.format(foreign_table_name))))
            # Why create a new variable "my_backref_name" here?
            # Because, all operations that introduce new names use the local scope, especially assignments.
            # Assign to backref_name will change it to a local variable which we don't want to, so we have to create a new variable.
            # reference: http://docs.python.org/tutorial/classes.html#python-scopes-and-namespaces
            my_backref_name = backref_name or '{0}s'.format(table_name)
            setattr(cls, foreign_name, relationship(foreign_model_name, 
                primaryjoin = '{0}.{1} == {2}.id'.format(model_name, foreign_key, foreign_model_name), 
                backref = backref(my_backref_name, lazy = 'dynamic')))
            return cls
        return ref_table

    @staticmethod
    def many_to_many(ref_table_name, ref_name = None, backref_name = None, middle_table_name = None):
        """Class Decorator, add a many-to-many relationship between two SQLAlchemy models.
        Parameters:
        ref_table_name is the destination table name, it is NOT the one which this method decorated on.
        ref_name is how this model reference the destination models.
        backref_name is how the destination model reference this model.
        middle_table_name is the middle table name of this many-to-many relationship.
        """
        ref_name = ref_name or '{0}s'.format(ref_table_name)
        ref_model_name = ref_table_name.capitalize()
        def ref_table(cls):
            table_name = cls.__name__.lower()
            my_middle_table_name = middle_table_name or '{0}_{1}'.format(table_name, ref_table_name)
            middle_table = Table(
                my_middle_table_name, Database.Base.metadata,
                Column('{0}_id'.format(table_name), Integer, ForeignKey('{0}.id'.format(table_name)), primary_key = True),
                Column('{0}_id'.format(ref_table_name), Integer, ForeignKey('{0}.id'.format(ref_table_name)), primary_key = True),
            )
            my_backref_name = backref_name or '{0}s'.format(table_name)
            setattr(cls, ref_name, relationship(ref_model_name, secondary = middle_table, 
                lazy = 'dynamic', backref = backref(my_backref_name, lazy = 'dynamic')))
            return cls
        return ref_table

    @staticmethod
    def self_many_to_many(ref_name, backref_name, middle_table_name):
        """Class decorator, add a self-referential many-to-many relationship to a model.
        Parameters:
        ref_name and backref_name is how this model reference itself from two opposite direction
        middle_table_name is the middle table name of this many-to-many relationship
        """
        def ref_table(cls):
            model_name = cls.__name__
            table_name = model_name.lower()
            middle_table = Table(
                middle_table_name, Database.Base.metadata,
                # left follow right
                Column('left_id', Integer, ForeignKey('{0}.id'.format(table_name)), primary_key = True),
                Column('right_id', Integer, ForeignKey('{0}.id'.format(table_name)), primary_key = True)
            )
            setattr(cls, ref_name, relationship(model_name, secondary = middle_table, 
                primaryjoin = cls.id == middle_table.c.left_id,
                secondaryjoin = cls.id == middle_table.c.right_id,
                lazy = 'dynamic', backref = backref(backref_name, lazy = 'dynamic')))
            return cls
        return ref_table

    @staticmethod
    def created_timestamp(cls):
        """Class decorator, add a timestamp field 'created' to the model"""
        cls.created = Column(DateTime, default = func.now(), nullable = False)
        return cls

    @staticmethod
    def inherit_mixin(parent, child_nickname):
        """Provide a mixin for Join Table Inheritance"""
        class BaseClass:
            @declared_attr
            def id(cls):
                return Column(Integer, ForeignKey('{0}.id'.format(parent.lower())), primary_key = True)

            @declared_attr
            def __mapper_args__(cls):
                return {'polymorphic_identity': child_nickname}

        return BaseClass
   
    @staticmethod
    def ref_grandchildren(child, grandchildren):
        """Reference grandchildren. In a join table inheritance, for example, 
        Post has children Question and Answer, and every Post belongs to a User. 
        Then you can 'user.posts', but you can't 'user.questions' unless you apply this class decorator to User.
        In another word, provides syntactic sugar 'user.questions' for 'user.posts.filter_by(type = "question")'
        """
        def property_generator(grandchild):
            return property(lambda self: getattr(self, child + 's').filter_by(type = grandchild))
        def class_decorator(cls):
            [setattr(cls, grandchild + 's', property_generator(grandchild)) for grandchild in grandchildren]
            return cls
        return class_decorator
