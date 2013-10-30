#!/usr/bin/env python
#coding=utf-8

import peewee
from playhouse.signals import Model as _model

class Db(object):
    
    fn = peewee.fn
    R = peewee.R
    RawQuery = peewee.RawQuery
    DoesNotExist = peewee.DoesNotExist
    
    class FixMySQLDatabase(peewee.MySQLDatabase):
        field_overrides = {
            'tinyint': 'TINYINT',
            'smallint': 'SMALLINT',
            'int': 'INTEGER',
            'boolean': 'BOOL',
            'float': 'FLOAT',
            'primary_key': 'INTEGER(10) UNSIGNED AUTO_INCREMENT',
            'small_primary_key': 'SMALLINT(6) UNSIGNED AUTO_INCREMENT',
            'tiny_primary_key': 'TINYINT(3) UNSIGNED AUTO_INCREMENT',
            'text': 'TEXT',
        }
    
    class PrimaryKeyField(peewee.PrimaryKeyField):
        pass
    
    class TinyPrimaryKeyField(peewee.PrimaryKeyField):
        db_field = 'tiny_primary_key'

    class SmallPrimaryKeyField(peewee.PrimaryKeyField):
        db_field = 'small_primary_key'
    
    class TinyIntegerField(peewee.Field):
        db_field = 'tinyint'
        template = '%(column_type)s(%(max_length)s) unsigned default %(dbdefault)s'
        
        def field_attributes(self):
            return {'max_length': 3, 'dbdefault': 0}
        
        def coerce(self, value):
            return int(value)
        
    class SmallIntegerField(peewee.Field):
        db_field = 'smallint'
        template = '%(column_type)s(%(max_length)s) unsigned default %(default)s'
        
        def field_attributes(self):
            return {'max_length': 6, 'default': 0}
        
        def coerce(self, value):
            return int(value)
    
    class IntegerField(peewee.Field):
        db_field = 'int'
        template = '%(column_type)s(%(max_length)s) unsigned default %(default)s'
        
        def field_attributes(self):
            return {'max_length': 10, 'default': 0}
        
        def coerce(self, value):
            return int(value)
    
    class CharField(peewee.CharField):
        template = '%(column_type)s(%(max_length)s) default ""'
    
    class TextField(peewee.TextField):
        pass
    
    class FloatField(peewee.FloatField):
        pass
    
    class DateField(peewee.DateField):
        pass

    def __init__(self,kw):
        self.config = kw
        self.load_database();
        self.Model = self.get_model_class()
        
    def load_database(self):
        self.db = self.config.pop('db')
        self.database = Db.FixMySQLDatabase(self.db, **self.config)
        
    def get_model_class(self):
        class BaseModel(_model):
            class Meta:
                database = self.database
        return BaseModel
                
    def connect(self):
        self.database.connect()
    
    def close(self):
        try:
            self.database.close()
        except:pass