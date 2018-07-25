# coding: utf-8
"""
Models for user,blog,comment
"""

__author__ = 'Master Wang'

import time, uuid

from orm import Model, StringField, BooleanField, FloatField, TextField

from orm import BinaryField, IntegerField, TimeStampField


def next_id():
    return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)


class UsersNote(Model):
    # 类映射的表名
    __table__ = 'users_note'

    # 定义类的属性到列的映射
    id = IntegerField(primary_key=True,  colType='int(11)', auto_fill=True)
    path = StringField(colType='varchar(800)')
    mate = StringField(colType='varchar(255)')
    mate_hash = BinaryField(colType='binary(20)')
    mate_order = IntegerField(colType='smallint')
    order = IntegerField(colType='int(11)')
    update_time = TimeStampField(auto_fill=True)
    format = StringField(colType='varchar(30)')
    data = StringField(colType='varchar(1200)')


class DataNote(Model):
    # 类映射的表名
    __table__ = 'text_data_note'

    # 定义类的属性到列的映射
    data = TextField(colType='mediumtext')
    data_hash = BinaryField(primary_key=True)
    quote = IntegerField(colType='mediumint', default=1)


class TableRegisterNote(Model):
    # 类映射的表名
    __table__ = 'table_register_note'

    # 定义类的属性到列的映射
    table = StringField(primary_key=True, colType='varchar(800)')
    last_order = IntegerField(colType='int', default=1)

class User(Model):
    # 类映射的表名
    __table__ = 'users'

    # 定义类的属性到列的映射
    id = StringField(primary_key=True, default=next_id, colType='varchar(50)')
    email = StringField(colType='varchar(50)')
    passwd = StringField(colType='varchar(50)')
    admin = BooleanField()
    name = StringField(colType='varchar(50)')
    image = StringField(colType='varchar(500)')
    created_at = FloatField(default=time.time)


class Blog(Model):
    __table__ = 'blogs'

    id = StringField(primary_key=True, default=next_id, colType='varchar(50)')
    user_id = StringField(colType='varchar(50)')
    user_name = StringField(colType='varchar(50)')
    user_image = StringField(colType='varchar(500)')
    name = StringField(colType='varchar(50)')
    summary = StringField(colType='varchar(200)')
    content = TextField()
    created_at = FloatField(default=time.time)


class Comment(Model):
    __table__ = 'comments'

    id = StringField(primary_key=True, default=next_id, colType='varchar(50)')
    blog_id = StringField(colType='varchar(50)')
    user_id = StringField(colType='varchar(50)')
    user_name = StringField(colType='varchar(50)')
    user_image = StringField(colType='varchar(500)')
    content = TextField()
    created_at = FloatField(default=time.time)
