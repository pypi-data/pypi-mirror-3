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
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, func


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
    def foreign_key(table):
        """Class decorator, add a foreign key to a SQLAlchemy model.
        Parameter table is the destination table, in a one-to-many relationship, table is the "one" side.
        """
        def ref_table(cls):
            setattr(cls, '{0}_id'.format(table), Column(Integer, ForeignKey('{0}.id'.format(table))))
            setattr(cls, table, relationship(table.capitalize(), 
                primaryjoin = '{0}.{1}_id == {2}.id'.format(cls.__name__, table, table.capitalize()), 
                backref = backref(cls.__name__.lower() + 's', lazy = 'dynamic')))
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
