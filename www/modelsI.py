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

class getClipActionNote(Model):
    # 类映射的表名
    __table__ = 'getClipAction_note'

    # 定义类的属性到列的映射
    id = IntegerField(primary_key=True,  colType='int(11)', auto_fill=True)
    path = StringField(colType='varchar(800)')
    mate = StringField(colType='varchar(255)')
    mate_hash = BinaryField(colType='binary(20)')
    mate_order = IntegerField(colType='smallint')
    order = IntegerField(colType='int(11)')
    update_time = TimeStampField(auto_fill=True)
    mate_format = StringField(colType='varchar(30)')
    data = StringField(colType='varchar(1200)')

class getAccountsDataNote(Model):
    # 类映射的表名
    __table__ = 'getAccountsData_note'

    # 定义类的属性到列的映射
    id = IntegerField(primary_key=True,  colType='int(11)', auto_fill=True)
    path = StringField(colType='varchar(800)')
    mate = StringField(colType='varchar(255)')
    mate_hash = BinaryField(colType='binary(20)')
    mate_order = IntegerField(colType='smallint')
    order = IntegerField(colType='int(11)')
    update_time = TimeStampField(auto_fill=True)
    mate_format = StringField(colType='varchar(30)')
    data = StringField(colType='varchar(1200)')

class getSmartFilingInfoNote(Model):
    # 类映射的表名
    __table__ = 'getSmartFilingInfo_note'

    # 定义类的属性到列的映射
    id = IntegerField(primary_key=True,  colType='int(11)', auto_fill=True)
    path = StringField(colType='varchar(800)')
    mate = StringField(colType='varchar(255)')
    mate_hash = BinaryField(colType='binary(20)')
    mate_order = IntegerField(colType='smallint')
    order = IntegerField(colType='int(11)')
    update_time = TimeStampField(auto_fill=True)
    mate_format = StringField(colType='varchar(30)')
    data = StringField(colType='varchar(1200)')

class getFilingInfoNote(Model):
    # 类映射的表名
    __table__ = 'getFilingInfo_note'

    # 定义类的属性到列的映射
    id = IntegerField(primary_key=True,  colType='int(11)', auto_fill=True)
    path = StringField(colType='varchar(800)')
    mate = StringField(colType='varchar(255)')
    mate_hash = BinaryField(colType='binary(20)')
    mate_order = IntegerField(colType='smallint')
    order = IntegerField(colType='int(11)')
    update_time = TimeStampField(auto_fill=True)
    mate_format = StringField(colType='varchar(30)')
    data = StringField(colType='varchar(1200)')

class getNotebooksNote(Model):
    # 类映射的表名
    __table__ = 'getNotebooks_note'

    # 定义类的属性到列的映射
    id = IntegerField(primary_key=True,  colType='int(11)', auto_fill=True)
    path = StringField(colType='varchar(800)')
    mate = StringField(colType='varchar(255)')
    mate_hash = BinaryField(colType='binary(20)')
    mate_order = IntegerField(colType='smallint')
    order = IntegerField(colType='int(11)')
    update_time = TimeStampField(auto_fill=True)
    mate_format = StringField(colType='varchar(30)')
    data = StringField(colType='varchar(1200)')

class getTagsNote(Model):
    # 类映射的表名
    __table__ = 'getTags_note'

    # 定义类的属性到列的映射
    id = IntegerField(primary_key=True,  colType='int(11)', auto_fill=True)
    path = StringField(colType='varchar(800)')
    mate = StringField(colType='varchar(255)')
    mate_hash = BinaryField(colType='binary(20)')
    mate_order = IntegerField(colType='smallint')
    order = IntegerField(colType='int(11)')
    update_time = TimeStampField(auto_fill=True)
    mate_format = StringField(colType='varchar(30)')
    data = StringField(colType='varchar(1200)')

class setSelectedAccountNote(Model):
    # 类映射的表名
    __table__ = 'setSelectedAccount_note'

    # 定义类的属性到列的映射
    id = IntegerField(primary_key=True,  colType='int(11)', auto_fill=True)
    path = StringField(colType='varchar(800)')
    mate = StringField(colType='varchar(255)')
    mate_hash = BinaryField(colType='binary(20)')
    mate_order = IntegerField(colType='smallint')
    order = IntegerField(colType='int(11)')
    update_time = TimeStampField(auto_fill=True)
    mate_format = StringField(colType='varchar(30)')
    data = StringField(colType='varchar(1200)')


class submissionDataNote(Model):
    # 类映射的表名
    __table__ = 'submission_data_note'

    # 定义类的属性到列的映射
    id = IntegerField(primary_key=True,  colType='int(11)', auto_fill=True)
    path = StringField(colType='varchar(800)')
    mate = StringField(colType='varchar(255)')
    mate_hash = BinaryField(colType='binary(20)')
    mate_order = IntegerField(colType='smallint')
    order = IntegerField(colType='int(11)')
    update_time = TimeStampField(auto_fill=True)
    mate_format = StringField(colType='varchar(30)')
    data = StringField(colType='varchar(1200)')

