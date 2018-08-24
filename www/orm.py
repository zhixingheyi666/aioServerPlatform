# coding: utf-8

__author__ = 'Master Wang'

import asyncio, aiomysql, pdb
import json

from mylog import logger
import copy, hashlib
import sys
# sysFc = 'D:\\python_learn\\sysFc'
# sys.path.append(sysFc)

# logger = crLog(fname = 'D:\桌面\orm.log')
# from logSf10 import logger
# logger = logger
import random

# self#
# 改造，用一个字典结构存储多个链接池，测试
__poollist = {}


# 查询  自增id(下一个autoincrement值)
# 参考网址 https://www.cnblogs.com/tommy-huang/p/5602125.html
@asyncio.coroutine
def select_autoincrement(table_name, cur=None, database="excodout"):
    sql = """SELECT auto_increment FROM information_schema.tables WHERE table_schema=? AND table_name=?"""
    # sql = """SELECT auto_increment FROM information_schema.tables where table_schema='fortest' and table_name='users_note'"""
    args = (database, table_name)
    # rs = yield from select(sql, args, database="fortest")
    rs = yield from select(sql, args, cur=cur, database=database)
    return rs[0]["auto_increment"]


@asyncio.coroutine
def create_pool(loop, **kw):
    logger.info('CREATE DATABASE connction pool...')
    # self#
    # 改造，用于每次调用按需生成不同链接池，测试
    global __poollist
    ipool = yield from aiomysql.create_pool(  # host = kw.get('host','127.0.0.1'),
        host=kw.get('host', 'localhost'), port=kw.get('port', 3306), user=kw['user'], password=kw['password'],
        db=kw['database'], charset=kw.get('charset', 'utf8'), autocommit=kw.get('autocommit', True),
        maxsize=kw.get('maxsize', 10), minsize=kw.get('minsize', 1), loop=loop)
    # 暂时用所要连接的数据库的名字命名不同的连接池，以后再完善命名方案
    __poollist[kw['database']] = ipool


# 函数的返回rs是一个list，这个list的每个元素是一个dict，对应于数据库表中的一行

@asyncio.coroutine
def select(sql, args, size=None, database='excodout'):
    log(sql, args)
    global __poollist
    with (yield from __poollist[database]) as conn:
        cur = yield from conn.cursor(aiomysql.DictCursor)
        yield from cur.execute(sql.replace('?', '%s'), args or ())
        if size:
            rs = yield from cur.fetchmany(size)
        else:
            rs = yield from cur.fetchall()
        yield from cur.close()
        logger.info('Rows returned: %s' % len(rs))
        return rs


@asyncio.coroutine
def execute_many(sql, args, autocommit=True, database='excodout'):
    log(sql)
    global __poollist
    with (yield from __poollist[database]) as conn:
        if not autocommit:
            yield from conn.begin()
        try:
            cur = yield from conn.cursor(aiomysql.DictCursor)
            yield from cur.executemany(sql.replace('?', '%s'), args)
            affected = cur.rowcount
            if not autocommit:
                yield from conn.commit()
                # yield from cur.colse()
        except BaseException as e:
            if not autocommit:
                yield from conn.rollback()
            raise
        return affected


@asyncio.coroutine
def execute(sql, args, autocommit=True, database='excodoout'):
    log(sql)
    with (yield from __poollist[database]) as conn:
        if not autocommit:
            yield from conn.begin()
        try:
            cur = yield from conn.cursor(aiomysql.DictCursor)
            yield from cur.execute(sql.replace('?', '%s'), args)
            affected = cur.rowcount
            if not autocommit:
                yield from conn.commit()
                # yield from cur.colse()
        except BaseException as e:
            if not autocommit:
                yield from conn.rollback()
            raise
        return affected


def log(sql, args=()):
    logger.info('SQL: %s' % sql)


def get_pool(database="excodout"):
    global __poollist
    return __poollist[database]


def format_data(mate_format, data, ex_map):
    if mate_format != "String":
        if mate_format == "Number":
            result = data
        elif mate_format == "Bool":
            # 下面两句是兼容旧的格式，新格式要求bool值需存储小写字符串以符合json的标准
            if data == "True":
                data = "true"
            elif data == "False":
                data = "false"
            result = data
        elif mate_format == "exStorage":
            try:
                result = json.dumps(ex_map[data])
            except BaseException as e:
                logger.warn(e)
                result = '"exStorage调试 -- > ' + data + '"'
            # result = '"' + ex_map[data] + '"'
        elif mate_format == "None":
            result = "null"
        elif mate_format == "Array":
            result = "[]"
        elif mate_format == "Object":
            result = "{}"
        else:
            try:
                data = str(data)
            except BaseException as e:
                logger.warn(e)
                data = str(e)
            result = '"临时调试 -- > ' + data + '"'
    else:
        # new_v = new_v + '"' + vv["data"] + '"' + ","
        result = '"' + data + '"'
    return result


def create_json(rows, step, left_print, ex_map, is_array=False, add_data={}, mate_order_map={}):
    json_result = ""
    skip = False
    while(len(left_print[0]) > 0):
        iter_print = left_print[0]
        for i in iter_print:
            left_print[0] = left_print[0][1:]
            if i == "{":
                #判断即将迭代的对象的是否是Array
                sub_is_array = False
                if len(left_print[0]) >0:
                    temp_step = step[0]
                    temp_array = 1
                    for li in left_print[0]:
                        if li == "}":
                            temp_array -= 1
                            if temp_array == 0:
                                if temp_step < len(rows):
                                    if rows[temp_step]["mate_format"] == "Array":
                                        sub_is_array = True
                                elif temp_step == len(rows):
                                    sub_is_array = is_array
                                break
                        elif li == "{":
                            temp_array += 1
                        else:
                            temp_step += 1
                # 递归迭代大括号里面子对象
                sub_json_value = create_json(rows, step, left_print, ex_map, sub_is_array, add_data, mate_order_map)
                if step[0] < len(rows):
                    if is_array is not True:
                        try:
                            # 这里rows的排序是从0开始的，所以其索引号比mate_order少 1，
                            # 但是mate_order_map是按照mate_order组成的键值对，所以引用的时候要加上1
                            # 例如rows108行对应的mate_order是109，所以对mate_order_map应取108+1的路径
                            remark = '\"' + rows[step[0]]["mate"] + '.' + add_data[mate_order_map[step[0]+1]][1:] + ','
                        except Exception:
                            # logger.warn(e)
                            remark = ""
                        json_result += remark
                        json_result += '\"' + rows[step[0]]["mate"] + '\"' + ':'
                    if sub_is_array is not True:
                        json_result += i
                    else:
                        json_result += "["
                    json_result += sub_json_value + ','
                    skip = True
                    break
                else:
                    if is_array is False:
                        json_result += i
                        # 如果有对象注释，并且生成了注释，那就将注释添加上
                        if -1 in add_data.keys():
                            json_result += add_data[-1] + ","
                        json_result += sub_json_value
                    else:
                        json_result += "["
                        if -1 in add_data.keys():
                            json_result += "{" + add_data[-1] + "}" + ","
                        json_result += sub_json_value[:-1] + "]"
                    return json_result
            elif i == ".":
                if not skip:
                    if is_array is not True:
                        try:
                            # 这里rows的排序是从0开始的，所以其索引号比mate_order少 1，
                            # 但是mate_order_map是按照mate_order组成的键值对，所以引用的时候要加上1
                            # 例如rows108行对应的mate_order是109，所以对mate_order_map应取108+1的路径
                            remark = '\"' + rows[step[0]]["mate"] + '.' + add_data[mate_order_map[step[0]+1]][1:] + ','
                        except Exception:
                            remark = ""
                        json_result += remark
                        json_result += '\"' + rows[step[0]]["mate"] + '\"' + ':'
                    json_result += format_data(rows[step[0]]["mate_format"], rows[step[0]]["data"], ex_map) + ','
                skip = False
                step[0] += 1
            elif i == "}":
                if is_array is not True:
                    json_result = json_result[:-1] + i
                else:
                    json_result = json_result[:-1] + "]"
                return json_result
            else:
                logger.warn("---------------||orm.py Func create_json: unexcept character \"%s\"in iterPrint" % i)


def create_args_string(num):
    L = []
    for n in range(num):
        L.append('?')
    return ','.join(L)


"""
check_symbol用以检查给定对象是否包含不支持的字符，
    例如本项目中，path不支持"."、双引号、单引号等
"""


def check_symbol(k, symbol=".,\"\'\\"):
    pass


# just for test
def print_rows(rows, num=0, recur=True):
    if not recur:
        for row in rows:
            if row[3] is not None:
                show = row[3][:30]
            else:
                show = "NoneType"
            print("\n" + row[0] + "\n" + row[1] + "\n" + str(row[5]) + "\n" + show + "......")
    else:
        for row in rows:
            if type(row) == dict:
                num += 1
                if row["data"] is not None:
                    show = row["data"][:30]
                else:
                    show = "NoneType"
                print("\n" + str(num) + "\n" + row["mate_format"] + "\n" + row["path"] + "\n" + show + "......")
            else:
                print_rows(row, num)


def ex_store(v, longText):
    vHash = hashlib.sha256(v.encode("utf-8")).hexdigest()
    if vHash in longText.keys():
        if v != longText[vHash]:
            logger.warn("---------||                    ||-----------------")
            logger.warn("---------||   惊现HASH碰撞!!    ||-----------------")
            logger.warn("---------||   惊现HASH碰撞!!    ||-----------------")
            logger.warn("---------||                    ||-----------------")
            logger.warn("+++++++++++++++++++++++++++++++++++++++++++++++++++")
            logger.warn(v)
            logger.warn("+++++++++++++++++++++++++++++++++++++++++++++++++++")
            logger.warn(longText[vHash])
            logger.warn("+++++++++++++++++++++++++++++++++++++++++++++++++++")
            longText[vHash] = v
    else:
        longText[vHash] = v
    v = vHash
    return v


def create_rows(rows, num, order, result, iter_print):
    for row in rows:
        if type(row) == dict:
            if "result" in row.keys():
                num[0] += 1
                final = row["result"] + [hashlib.sha1(row["result"][0].encode("utf-8")).digest(), num[0], order]
                iter_print = iter_print + "."
            elif "add" in row.keys():
                final = row["add"][:-1] + [hashlib.sha1(row["add"][0].encode("utf-8")).digest(), row["add"][-1:], order]
            result.append(final)
        else:
            iter_print = iter_print + create_rows(row, num, order, result, "{")
    iter_print = iter_print + "}"
    return iter_print


"""
0.迭代处理obj，obj将成为数组，他的每个mate将成为数组的一个元素，
    如果obj是嵌套的，迭代出的数组也是嵌套的。
1.当传入的obj的值不是dict或者array，即obj是string、int、float、bool类型，经测试iterObj会按照既定程序，
    向数据库插入mate_order为-2，mate值为notObj，path为[[table name]].notObj的，形式如下的行
        '128', 'table_for_test.notObj', 'notObj', ?, '-2', '128', '2018-08-14 15:18:57', 'Number', '3.1415926'
2.当传入的obj的值是空dict或者空array，
    向数据库插入mate_order为-2，mate值为emptyObj，path为[[table name]].emptyObj的，形式如下的行
        '128', 'table_for_test.emptyObj', 'emptyObj', ?, '-2', '128', '2018-08-14 15:18:57', 'Dcit', None

"""


def iterObj(obj, rows, path, longText, table=None):
    # 如果最开始的Object是个Array，为了避免还原时出错，需要判定并返回一开始的Object类型,
    # 用变量obj_format标记吧
    obj_format = "object"
    child_rows = []
    if type(obj) == dict:
        for k, v in obj.items():
            mate = str(k)
            this_path = path + "." + mate
            mate_format = "NoneType"
            data = None
            if check_symbol(k):
                pass
            elif type(v) == dict:
                mate_format = "Object"
                data = len(v)
                iterObj(v, child_rows, this_path, longText)
            elif type(v) == list:
                mate_format = "Array"
                data = len(v)
                iterObj(v, child_rows, this_path + ".", longText)
            elif type(v) == str:
                mate_format = "String"
                # todo : 这里需要添加一个判定数据长度的函数，和一段长数据转储程序
                """
                我感觉也可以在sql内部用触发器去实现转储和引用计数，
                暂时重心不在这边，所以写一个超长截取的临时代码
                """
                # if len(v) > 1200:
                if len(v) > 120:
                    v = ex_store(v, longText)
                    mate_format = "exStorage"
                    """
                    vHash = hashlib.sha256(v.encode("utf-8")).digest()
                    if vHash in longText.keys():
                        if v != longText[vHash]:
                            logger.warn("---------||                    ||-----------------")
                            logger.warn("---------||   惊现HASH碰撞!!    ||-----------------")
                            logger.warn("---------||   惊现HASH碰撞!!    ||-----------------")
                            logger.warn("---------||                    ||-----------------")
                            logger.warn("+++++++++++++++++++++++++++++++++++++++++++++++++++")
                            logger.warn(v)
                            logger.warn("+++++++++++++++++++++++++++++++++++++++++++++++++++")
                            logger.warn(longText[vHash])
                            logger.warn("+++++++++++++++++++++++++++++++++++++++++++++++++++")
                            longText[vHash] = v
                    else:
                        longText[vHash] = v
                    v = vHash
                    # v = v[:1200]
                    # mate_format = "CUT CUT"
                    """
                data = v
            elif type(v) == float or type(v) == int:
                mate_format = "Number"
                data = str(v)
            elif type(v) == bool:
                mate_format = "Bool"
                data = str.lower(str(v))
            elif v is None:
                mate_format = "None"
                data = None
            else:
                # 数据类型超出处理范围应当报错
                pass
            # row = {"path": this_path, "mate_format": mate_format, "mate": mate, "data": data}
            row = {"result": [this_path, mate_format, mate, data]}
            child_rows.append(row)
        # path为空字符串，是第一次迭代的标志
        if path == "":
            if len(obj) == 0:
                mate = "emptyObj"
                this_path = "." + mate
                mate_format = "Object"
                mate_order = -0
                data = 0
                # 为了形式上的统一，将结果放在list中
                child_rows = [{"add": [this_path, mate_format, mate, data, mate_order]}]
    elif type(obj) == list:
        for k, v in enumerate(obj):
            mate = str(k)
            this_path = path + "." + mate
            mate_format = "NoneType"
            data = None
            if check_symbol(k):
                pass
            elif type(v) == dict:
                mate_format = "Object"
                data = len(v)
                iterObj(v, child_rows, this_path, longText)
            elif type(v) == list:
                mate_format = "Array"
                data = len(v)
                iterObj(v, child_rows, this_path + ".", longText)
            elif type(v) == str:
                mate_format = "String"
                # todo : 这里需要添加一个判定数据长度的函数，和一段长数据转储程序
                """
                我感觉也可以在sql内部用触发器去实现转储和引用计数，
                暂时重心不在这边，所以写一个超长截取的临时代码
                """
                # if len(v) > 1200:
                if len(v) > 120:
                    v = ex_store(v, longText)
                    mate_format = "exStorage"
                    # v = v[:1200]
                    # mate_format = "CUT CUT"
                data = v
            elif type(v) == float or type(v) == int:
                mate_format = "Number"
                data = str(v)
            elif type(v) == bool:
                mate_format = "Bool"
                data = str.lower(str(v))
            elif v is None:
                mate_format = "None"
                data = None
            else:
                # 数据类型超出处理范围应当报错
                pass
            row = {"result": [this_path, mate_format, mate, data]}
            # row = {"path": this_path, "mate_format": mate_format, "mate": mate, "data": data}
            child_rows.append(row)
        # path为空字符串，是第一次迭代的标志
        if path == "":
            if len(obj) == 0:
                mate = "emptyObj"
                this_path = "." + mate
                mate_format = "Array"
                mate_order = -0
                data = 0
                # 为了形式上的统一，将结果放在list中
                child_rows = [{"add": [this_path, mate_format, mate, data, mate_order]}]
            else:
                obj_format = "Array"
    else:
        mate = "notObj"
        this_path = table + "." + mate
        mate_format = "NoneType"
        data = None
        # 对象的附加信息是基于mate_order区别的，当mate_order的值为负，表示此信息非对象原生，而是附加信息
        # 不同负数值的具体含义，参见自定义的数据库说明文档，-2表示传进来的对象不是标准的对象格式(严格的说，不是
        # dict或者list),这里考虑最大的兼容性，采用附加信息的方式存储
        mate_order = -0
        if type(obj) == str:
            mate_format = "String"
            # todo : 这里需要添加一个判定数据长度的函数，和一段长数据转储程序
            """
            我感觉也可以在sql内部用触发器去实现转储和引用计数，
            暂时重心不在这边，所以写一个超长截取的临时代码
            """
            # if len(obj) > 1200:
            if len(obj) > 120:
                obj = ex_store(obj, longText)
                mate_format = "exStorage"
                # obj = obj[:1200]
                # mate_format = "CUT CUT"
            data = obj
        elif type(obj) == float or type(obj) == int:
            mate_format = "Number"
            data = str(obj)
        elif type(obj) == bool:
            mate_format = "Bool"
            data = str.lower(str(obj))
        elif obj is None:
            mate_format = "None"
            data = None
        else:
            # 数据类型超出处理范围应当报错
            pass
        # 为了形式上的统一，将结果放在list中
        child_rows = [{"add": [this_path, mate_format, mate, data, mate_order]}]
    rows.append(child_rows)
    return obj_format


"""
# 首次在python中自编闭包形式的函数，虽然最后用不到了，留作纪念
def create_insert_string(tableName, primaryKey):
    def func(tableName, primaryKey):
        def insert_string(self, columns, escapes):
            # escaped_fields = list(map(lambda f: '`%s`' % f, fields))
            columns = copy.copy(columns)
            if primaryKey not in columns:
                columns.append(primaryKey)
            fields = list(map(lambda f: '`%s`' % f, filter(lambda x: x not in escapes, columns)))
            sql = 'insert into `%s` (%s) values (%s)' % (
                tableName, ','.join(fields), create_args_string(len(fields)))
            return sql
        return insert_string
    return func(tableName, primaryKey)

"""


class Field(object):
    def __init__(self, name, column_type, primary_key, default, auto_fill):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        # auto_fill是数据库自动填充的，例如id的autoincrement，或者timestamp，或者建立table时候的default值
        # 而这里的default是orm创建table到相应class类映射的时候设定的，下面的写法是以这个设定优先
        if default is not None:
            self.default = default
            self.auto_fill = False
        else:
            self.default = default
            self.auto_fill = auto_fill

    def __str__(self):
        return '<%s, %s:%s>' % (self.__class__.__name__, self.column_type, self.name)


class StringField(Field):
    def __init__(self, name=None, primary_key=False, default=None, colType='varchar(100)', auto_fill=False):
        super().__init__(name, colType, primary_key, default, auto_fill)


class BooleanField(Field):
    def __init__(self, name=None, default=None, auto_fill=False):
        super().__init__(name, 'boolean', False, default, auto_fill)


class IntegerField(Field):
    def __init__(self, name=None, primary_key=False, default=None, colType='bigint', auto_fill=False):
        super().__init__(name, colType, primary_key, default, auto_fill)


class BinaryField(Field):
    def __init__(self, name=None, primary_key=False, default=None, colType='binary(16)', auto_fill=False):
        super().__init__(name, colType, primary_key, default, auto_fill)


class TimeStampField(Field):
    def __init__(self, name=None, primary_key=False, default=None, colType='timestamp', auto_fill=False):
        super().__init__(name, colType, primary_key, default, auto_fill)


class FloatField(Field):
    def __init__(self, name=None, primary_key=False, default=None, colType='real', auto_fill=False):
        super().__init__(name, colType, primary_key, default, auto_fill)


class TextField(Field):
    def __init__(self, name=None, default=None, colType='text', auto_fill=False):
        super().__init__(name, colType, False, default, auto_fill)


class ModelMetaclass(type):
    """
    这里可以看出，ModelMetaclass这里的写法，就是提供了一种修改class属性的途径，attrs
    是传进来的class的属性的一个dict?
    创建class时候，把这个作为参数传递进去
    就会用这里编写的方法对要创建的class进行指定的修改
    """

    def __new__(cls, name, bases, attrs):
        # 排除Model类本身
        if name == 'Model':
            return type.__new__(cls, name, bases, attrs)
        # 获取table名称：
        tableName = attrs.get('__table__', None) or name
        logger.info('Found mode: %s (table: %s)' % (name, tableName))
        # 获取所有的Field和主键名称
        mappings = dict()
        fields = []
        primaryKey = None
        for k, v in attrs.items():
            if isinstance(v, Field):
                logger.info('Found mapping: %s --> %s' % (k, v))
                """
                #SF#每个数据库表对应的一个类，表的每个列，对应一个属性
                列对应的属性在这里就是Feild，也是一个Feild类的实例
                最后通过这里的mateclass
                把Feild实例整理存储在一个__mapping__的dict结构中
                """
                mappings[k] = v
                if v.primary_key:
                    # 找到主键：
                    if primaryKey:
                        raise RuntimeError('Duplicated primary key for field: %s' % k)
                    primaryKey = k
                else:
                    fields.append(k)
        if not primaryKey:
            raise RuntimeError('Primary key not found.')
        for k in mappings.keys():
            attrs.pop(k)
        escaped_fields = list(map(lambda f: '`%s`' % f, fields))
        attrs['__mappings__'] = mappings  # 保存属性和映射的关系
        attrs['__escape_column__'] = set()
        attrs['__table__'] = tableName
        attrs['__exStorage__'] = "text_data_note"
        attrs['__primary_key__'] = primaryKey  # 主键属性名
        # 这里的fields采用list是因为后面sql语句中要与参数位置一一对应，需要有确定的顺序
        attrs['__fields__'] = fields  # 除主键外的属性名
        # 构造默认的SELECT, INSERT, UPDATE和DELETE语句:
        attrs['__select__'] = 'select `%s`, %s from `%s`' % (primaryKey, ','.join(escaped_fields), tableName)
        attrs['__insert__'] = 'insert into `%s` (%s, `%s`) values (%s)' % (
        tableName, ','.join(escaped_fields), primaryKey, create_args_string(len(escaped_fields) + 1))
        attrs['__update__'] = 'update `%s` set %s where `%s` = ?' % (
        tableName, ','.join(map(lambda f: '`%s` = ?' % (mappings.get(f).name or f), fields)), primaryKey)
        attrs['__delete__'] = 'delete from %s where `%s` = ? ' % (tableName, primaryKey)
        return type.__new__(cls, name, bases, attrs)


class Model(dict, metaclass=ModelMetaclass):
    def __init__(self, **kw):
        super(Model, self).__init__(**kw)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' has no attribute %s" % key)

    def __setattr__(self, key, value):
        self[key] = value

    """
    # SF：本函数扩充了对数据库中含有自动填充的列
    # （例如auto increment，timestamp）的表
    #  生成insert语句的支持
    """

    def create_insert_string(self, columns=[], escapes=[]):
        if not columns and not escapes:
            columns = copy.copy(self.__fields__)
            escapes = self.__escape_column__
            if self.__primary_key__ not in columns:
                columns.append(self.__primary_key__)
        fields = list(map(lambda f: '`%s`' % f, filter(lambda x: x not in escapes, columns)))
        sql = 'insert into `%s` (%s) values (%s)' % (self.__table__, ','.join(fields), create_args_string(len(fields)))
        return sql

    def getValue(self, key):
        """
        现在已经建立了程序按行入库的框架，因此我组织程序的方式可以有新的变革
            例如，在程序中插入类似xml的标签或者id，以实现某些搜索或标记的需求或新功能
            这里，我想提示自己稍后详细研究下函数getattr，我就可以标记如下：
            #梗#稍后研究下面的 getattr
        """
        return getattr(self, key, None)

    def getValueOrDefault(self, key):
        auto_fill = False
        if key in self.__escape_column__:
            self.__escape_column__.discard(key)
        # todo:由于列名对应实例的属性，所以实例的其他属性和函数名不能和列名相同
        #       或者说列名不能和实例一般属性以及函数重名
        value = getattr(self, key, None)
        if value is None:
            field = self.__mappings__[key]
            if field.default is not None:
                value = field.default() if callable(field.default) else field.default
                logger.info('Using default value for %s: %s' % (key, str(value)))
                setattr(self, key, value)
            elif field.auto_fill is True:
                self.__escape_column__.add(key)
                auto_fill = True
                logger.info('Using database auto fill value for %s: %s' % (key, str(value)))
        return [value, auto_fill]

    @classmethod
    @asyncio.coroutine
    def get_object(cls, *, order=None, json_string=True, include_remark=True, **kw):
        database = "fortest"
        pool = get_pool(database)
        with (yield from pool) as conn:
            yield from conn.begin()
            try:
                cur = yield from conn.cursor(aiomysql.DictCursor)
                if order is None:
                    """
                    ··aiomysql pymysql
                        在拼接sql查询语句的时候，
                            table的名字不能够作为查询的参数
                        必须提前在查询语句中用字串拼接好，所以下面语句会报错
                        # yield from cur.execute("SELECT max(`order`) FROM %s", cls.__table__)
                    """
                    yield from cur.execute("""SELECT max(`order`) FROM %s""" % cls.__table__)
                    order = yield from cur.fetchall()
                    order = order[0]["max(`order`)"]
                """
                1.获取对象原生信息
                2.获取对象附加信息，分别处理不同类型的附加信息
                3.将获取的信息组合成json字串或者python的dict对象结构
                4.返回结果
                """
                # 根据需要，获取对象附加信息
                add_data = {}
                mate_order_map = {}
                if include_remark:
                    sql = "select * from %s " % cls.__table__ + "where `mate_order` < 0 order by `mate_order`"
                    yield from cur.execute(sql)
                    add_pre_rows = yield from cur.fetchall()
                    ex_storage = []
                    iter_print = {}
                    """
                         # 附加信息如果有相同的mate_order,我们视为同一条附加信息，
                         # 同一条附加信息也应当由相同的mate
                    """
                    for pre_row in add_pre_rows:
                        if pre_row["mate_order"] > -10000:
                            # 如果正常执行saveObj写入程序，得到的path一定是字符串，这里将其设为数字-1，后面
                            # 就很容易与其他mate注释的path区分开，path值是一个整数-1的，就是整个Object的注释
                            pre_row["path"] = -1
                            pre_row["mate_order"] = -1
                        pre_path = pre_row["path"]
                        pre_mate = pre_row["mate"]

                        # pre_path用来区分注释属于对象的哪一个mate，
                        # pre_mate用来区分同一个mate的不同条目的注释，
                        # order用来区分同一条注释的前后更新
                        def ex_hand(pre_row):
                            if pre_row["mate_format"] == "exStorage":
                                ex_storage.append(pre_row["data"])

                        if pre_path not in add_data.keys():
                            add_data[pre_path] = {}
                            add_data[pre_path][pre_mate] = pre_row
                            ex_hand(pre_row)
                        elif pre_mate not in add_data[pre_path].keys():
                            add_data[pre_path][pre_mate] = pre_row
                            ex_hand(pre_row)
                            # 因为附加信息的order存储时候取反成了负数，所以order值较小的是新的信息
                            # 将覆盖旧的信息
                        elif add_data[pre_path][pre_mate]["order"] > pre_row["order"]:
                            add_data[pre_path][pre_mate] = pre_row
                            ex_hand(pre_row)
                        """
                        # 大于-10000部分为整个对象的注释
                        if pre_order > -10000:
                            if pre_order not in object_add_data.keys():
                                object_add_data[pre_order] = pre_row
                            elif object_add_data[pre_order]["order"] > pre_row["order"]:
                                object_add_data[pre_order] = pre_row
                        else:
                        """

                    # 获取path对应的mate_order编号
                    sql = "select `mate_order` from %s" % cls.__table__ + " where `order` = %s and `path` = %s"
                    for p in add_data.keys():
                        yield from cur.execute(sql, (order, p))
                        mate_order = yield from cur.fetchall()
                        if mate_order:
                            mate_order_map[mate_order[0]["mate_order"]] = p
                    # 提取exStorage存储的数据
                    ex_map_remark = {}
                    for ex in ex_storage:
                        sql = "select `data` from %s" % cls.__exStorage__ + " where `data_hash` = %s"
                        yield from cur.execute(sql, (ex))
                        ex_data = yield from cur.fetchall()
                        if ex_data:
                            ex_map_remark[ex] = ex_data[0]["data"]

                    # 构成json字串
                    for k, v in add_data.items():
                        new_v = '"..remark":{'
                        for kk, vv in v.items():
                            new_v = new_v + '"' + kk + '"' + ':'
                            mate_data = format_data(vv["mate_format"], vv["data"], ex_map_remark)
                            new_v = new_v + mate_data + ","
                        new_v = new_v[:-1] + "}"
                        add_data[k] = new_v

                # 获取原生对象是否是非空Array
                is_array = False
                sql = "select mate_format, `data` from %s" % cls.__table__ + " where `mate` = 'arrayObject' and `order`= %s "
                yield from cur.execute(sql, (-order))
                # is_array = yield from cur.fetchone()
                is_array = yield from cur.fetchall()
                if len(is_array) == 1:
                    is_array = True
                else:
                    is_array = False
                #获取迭代指纹
                sql = "select mate_format, `data` from %s" % cls.__table__ + " where `mate_order` = -2 and `order` = %s "
                yield from cur.execute(sql, (-order,))
                iter_print = yield from cur.fetchone()
                if iter_print["mate_format"] == "exStorage":
                    sql = "select `data` from %s" % cls.__exStorage__ + " where `data_hash` = %s"
                    yield from cur.execute(sql, (iter_print["data"],))
                    iter_print["data"] = yield from cur.fetchone()
                    iter_print["data"] = iter_print["data"]["data"]
                # 获取存储在外部的数据(exStorage)
                sql = "select `data` from %s " % cls.__table__ + "where `order` = %s and `mate_format` = 'exStorage'"
                yield from cur.execute(sql, order)
                origin_ex_storages= yield from cur.fetchall()
                # 提取exStorage存储的数据
                ex_map = {}
                for ex in origin_ex_storages:
                    sql = "select `data` from %s" % cls.__exStorage__ + " where `data_hash` = %s"
                    yield from cur.execute(sql, (ex["data"]))
                    ex_data = yield from cur.fetchall()
                    if ex_data:
                        ex_map[ex["data"]] = ex_data[0]["data"]


                # 获取对象原生信息
                sql = "select * from %s " % cls.__table__ + "where `order` = %s order by `mate_order`"
                yield from cur.execute(sql, order)
                origin_pre_rows = yield from cur.fetchall()
                # 构成json对象
                count_row_num = [0, ]
                if len(origin_pre_rows) is 1:
                    if origin_pre_rows[0]["mate_order"] is 0:
                        object_json = format_data(origin_pre_rows[0]["mate_format"], origin_pre_rows[0]["data"], ex_map)
                        if -1 in add_data.keys():
                            if object_json == "{}":
                                object_json = "{" + add_data[-1] + "}"
                            elif object_json == "[]":
                                # 本来Array的注释只能添加在Array的外头，但是Array外面没有其他了，
                                # 所以考虑最外层如果时个Array，整个对象的注释应该怎样添加呢？
                                # 规定采用如下格式吧
                                object_json = '{"..Object":' + object_json + "," + add_data[-1] + "}"
                                pass
                            else:
                                object_json = '{"..Object":' + object_json + "," + add_data[-1] + "}"
                else:
                    object_json = create_json(origin_pre_rows, count_row_num, [iter_print["data"]], ex_map, is_array, add_data, mate_order_map)

            except BaseException as e:
                logger.warn(e)
                pass
        """
            tips_SF:这里返回json字串中，每一个键和非Object非Array的值，必须用双引号，整个字符串用单引号包裹，
            下面的样子会导致解析错误
            return "{'..remark': {'algorithm': 'algorithm', 'ele': 'lll', 'theta': 'theta'},'colon equals': {'..remark': 'to denote setting a variable on the left hand side','style': ':='}, 'gradient': 'gradient descent', 'notation': {'colon': ':'}}"
        # return '{' + add_data[-1] + '}'
        # return '{"..remark": {"algorithm": "algorithm", "ele": "lll", "theta": "theta"},"colon equals": {"..remark": "to denote setting a variable on the left hand side","style": ":="}, "gradient": "gradient descent", "notation": {"colon": ":"}}'
        # return   '{"gradient": "gradient descent", "..remark": {"algorithm": "algorithm", "ele": "lll", "theta": "theta"}, "not ation": {"colon": ":"}, "colon equals": {"style": ":=", "..remark": "to denote setting a variable on the left hand side "}}'
        """
        return object_json

    """
    # saveObj函数接收一个由json转化来的对象，相应代码如下：
        .文件coroweb.py中
            params = yield from request.text()
                    try:
                        params = json.loads(params)
    # saveObj采用递归迭代的方式，将对象分解成一个个mate(元)，以及必要信息
        每个mate对应一行，存储到数据库中
    # saveObj是所有json转化来的对象都应该是通用的，应该是通用方法
    # ·显然，本方法是有特异性的，针对的是<存储Obj>的表格
            这些表格的列必须包含如下固定格式
                path, mate, mate_hash, mate_order, order, mate_format, data
    """

    @classmethod
    @asyncio.coroutine
    def saveObj(cls, obj, **kw):
        database = "fortest"
        pool = get_pool(database)
        with (yield from pool) as conn:
            yield from conn.begin()
            try:
                cur = yield from conn.cursor(aiomysql.DictCursor)
                # 首先执行必要的检查，包括对表格是否是<存储Obj>的表格的检查
                OBJTABLE = ["path", "mate_format", "mate", "data", "mate_hash", "mate_order", "order"]
                if not set(OBJTABLE) <= set(cls.__fields__ + [cls.__primary_key__]):
                    rs = "-----|| This is %s.saveObj||---( Failed,Model must be kind of <Obj saved table> ! )" \
                         "--------------------------" % cls.__table__
                    logger.warn(rs)
                else:
                    rows_pre = []
                    long_text = {}
                    obj_format = iterObj(obj, rows_pre, "", long_text, cls.__table__)

                    def insert_ex_table(data_hash, data):
                        logger.info("--------------||This is insert_ex_table||-------------------------")
                        # todo: 新值插入，旧值增加引用计数测试成功，只有抛出错误需要修正
                        yield from cur.execute(
                            """SELECT  `data`,`data_hash`,`quote` FROM text_data_note WHERE `data_hash` = %s""", data_hash)
                        query_rows = yield from cur.fetchall()
                        if not query_rows:
                            yield from cur.execute(
                                """INSERT INTO text_data_note( `data`,`data_hash`,`quote` ) VALUES( %s,%s,%s)""",
                                (data, data_hash, 1))
                        else:
                            if query_rows[0]["data"] == data:
                                new_quote = query_rows[0]["quote"] + 1
                                yield from cur.execute(
                                    """UPDATE text_data_note SET `quote` = %s WHERE `data_hash` = %s """,
                                    (new_quote, query_rows[0]["data_hash"]))
                            else:
                                # SF:最好编写一个正规的错误类型
                                raise RuntimeError("""-------------||                ||-----------------
                                -------------|| 发现Hash碰撞！！||-----------------
                                -------------||                 ||-----------------
                                -------------||%s||-----------------
                                -------------||%s||-----------------
                                -------------||%s||-----------------""" % (data, query_rows[0]["data"], data_hash))

                    # long_text_len = len(long_text)
                    # logger.warn("++++++++++++++||length of longText: %d+++++++++++++++++++++++++++++++++++++++++++++++++++" % long_text_len)
                    for data_hash, data in long_text.items():
                        # logger.info("--------------||This is insert_ex_table||-------------------------")
                        # todo: 新值插入，旧值增加引用计数测试成功，只有抛出错误需要修正
                        yield from cur.execute(
                            """SELECT  `data`,`data_hash`,`quote` FROM text_data_note WHERE `data_hash` = %s""", data_hash)
                        query_rows = yield from cur.fetchall()
                        if not query_rows:
                            yield from cur.execute(
                                """INSERT INTO text_data_note( `data`,`data_hash`,`quote` ) VALUES( %s,%s,%s)""",
                                (data, data_hash, 1))
                        else:
                            if query_rows[0]["data"] == data:
                                new_quote = query_rows[0]["quote"] + 1
                                yield from cur.execute(
                                    """UPDATE text_data_note SET `quote` = %s WHERE `data_hash` = %s """,
                                    (new_quote, query_rows[0]["data_hash"]))
                            else:
                                # SF:最好编写一个正规的错误类型
                                raise RuntimeError("""-------------||                ||-----------------
                                -------------|| 发现Hash碰撞！！||-----------------
                                -------------||                 ||-----------------
                                -------------||%s||-----------------
                                -------------||%s||-----------------
                                -------------||%s||-----------------""" % (data, query_rows[0]["data"], data_hash))
                    # todo: 这里有一个BUG
                    """
                        这里写的代码是异步代码，也就是对并发支持度高，对于读取来说
                        并不会产生问题，但是对于写入，如果写入的某些值是基于前面
                        的运行结果，那么就会出错。例如一个写入的程序还没执行完毕，
                        另一个写入程序获得的auto inrement的值就可能是"老"的值，
                        这显然是个错误。
                            看来写入，能不能并发，该不该并发，都要好好研究考虑
                    """
                    yield from cur.execute(
                        """SELECT auto_increment FROM information_schema.tables WHERE table_schema=%s AND table_name=%s""",
                        (database, cls.__table__))
                    order = yield from cur.fetchall()
                    order = order[0]["auto_increment"]
                    # order = yield from select_autoincrement(cls.__table__, database="fortest")
                    rows_in = []
                    iter_print_row = []
                    iter_print = create_rows(rows_pre[0], [0, ], order, rows_in, "{")
                    iter_print_data = iter_print
                    iter_print_format = "String"
                    if len(iter_print) > 120:
                        iter_print_data= ex_store(iter_print, long_text)
                        # logger.info("--------------||This is insert_ex_table||-------------------------")
                        # todo: 新值插入，旧值增加引用计数测试成功，只有抛出错误需要修正
                        yield from cur.execute(
                            """SELECT  `data`,`data_hash`,`quote` FROM text_data_note WHERE `data_hash` = %s""", iter_print_data)
                        query_rows = yield from cur.fetchall()
                        if not query_rows:
                            yield from cur.execute(
                                """INSERT INTO text_data_note( `data`,`data_hash`,`quote` ) VALUES( %s,%s,%s)""",
                                (iter_print, iter_print_data, 1))
                        else:
                            if query_rows[0]["data"] == iter_print:
                                new_quote = query_rows[0]["quote"] + 1
                                yield from cur.execute(
                                    """UPDATE text_data_note SET `quote` = %s WHERE `data_hash` = %s """,
                                    (new_quote, query_rows[0]["data_hash"]))
                            else:
                                # SF:最好编写一个正规的错误类型
                                raise RuntimeError("""-------------||                ||-----------------
                                -------------|| 发现Hash碰撞！！||-----------------
                                -------------||                 ||-----------------
                                -------------||%s||-----------------
                                -------------||%s||-----------------
                                -------------||%s||-----------------""" % (iter_print, query_rows[0]["data"], iter_print_data))
                        iter_print_format = "exStorage"
                    iter_print_row = [".iterPrint", iter_print_format, "iterPrint", iter_print_data,
                                      hashlib.sha1(".iterPrint".encode("utf-8")).digest(), -2, -order]
                    if obj_format == "Array":
                        rows_in.append([".arrayObject", "Array", "arrayObject", str(len(obj)),
                                        hashlib.sha1(".arrayObject".encode("utf-8")).digest(), 0, -order])
                    rows_in.append(iter_print_row)
                    # print_rows(rows_in, recur=False)
                    fields = list(map(lambda f: '`%s`' % f, OBJTABLE))
                    sql = 'insert into `%s` (%s) values (%s)' % (
                    cls.__table__, ','.join(fields), create_args_string(len(OBJTABLE)))
                    # rs = yield from execute_many(sql, rows_in, database="fortest")
                    yield from cur.executemany(sql.replace('?', '%s'), rows_in)
                    rs = cur.rowcount
                    rs = "-----|| This is %s.saveObj||---(Insert %s rows...)--------------------------" % (
                    cls.__table__, rs)
                    logger.info(rs)
                    # return rows_in
                    yield from conn.commit()
                    # yield from cur.colse()
                    return rs
            except BaseException as e:
                yield from conn.rollback()
                raise

    @classmethod
    @asyncio.coroutine
    def findAll(cls, where=None, args=None, **kw):
        'find objects by where clause.'
        sql = [cls.__select__]
        if where:
            sql.append('where')
            sql.append(where)
        if args is None:
            args = []
        orderBy = kw.get('orderBy', None)
        if orderBy:
            sql.append('order by')
            sql.append(orderBy)
        limit = kw.get('limit', None)
        if limit is not None:
            sql.append('limit')
            if isinstance(limit, int):
                sql.append('?')
                args.append(limit)
            elif isinstance(limit, tuple) and len(limit) == 2:
                sql.append('?, ?')
                args.extend(limit)
            else:
                raise ValueError('Invalid limit value: %s' % str(limit))
        rs = yield from select(' '.join(sql), args)
        # 梗#弄清cls(**r)是什么用法
        return [cls(**r) for r in rs]

    @classmethod
    @asyncio.coroutine
    def findNumber(cls, selectField, where=None, args=None):
        'find number by selected and where'
        # 梗#`%s`是什么用法
        # 这的_num是sql语句中的"别名"，查询某一列，然后给这一列起了个别名_num_，查询结果的列名直接就是这个别名了
        sql = ['select %s _num_ from `%s`' % (selectField, cls.__table__)]
        if where:
            sql.append('where')
            sql.append(where)
        rs = yield from select(' '.join(sql), args, 1)
        if len(rs) == 0:
            return None
        return rs[0]['_num_']

    @classmethod
    @asyncio.coroutine
    def find(cls, pk):
        # find object by primary key.
        rs = yield from select('%s where `%s` = ?' % (cls.__select__, cls.__primary_key__), [pk], 1)
        if len(rs) == 0:
            return None
        return cls(**rs[0])

    @asyncio.coroutine
    def save(self):
        pre_args = list(map(self.getValueOrDefault, self.__fields__))
        pre_args.append(self.getValueOrDefault(self.__primary_key__))
        args = []
        # 这pre_args的返回值是list，第一个元素是相应列的value值，第二个元素如果是
        # False表示这个元素不是数据库自动填充的，所以将其value添加进参数列表args
        for arg in pre_args:
            if arg[1] is False:
                args.append(arg[0])
        # creat_sql = self.__insert__
        sql = self.create_insert_string()
        rows = yield from execute(sql, args, database="fortest")
        while len(self.__escape_column__):
            self.__escape_column__.pop()
        # rows = yield from execute(self.__insert__(self.__fields__, self.__escape_column__), args)
        if rows != 1:
            logger.warn('Failed to insert record: affected rows: %s' % rows)

    @asyncio.coroutine
    def update(self):
        args = list(map(self.getValueOrDefault, self.__fields__))
        args.append(self.getValueOrDefault(self.__primary_key__))
        rows = yield from execute(self.__update__, args)
        if rows != 1:
            logger.warn('Failed to update by primary key: affected rows: %s' % rows)

    @asyncio.coroutine
    def remove(self):
        args = [self.getValue(self.__primary_key__)]
        rows = yield from execute(self.__delete__, args)
        if rows != 1:
            logger.warn('Failed to remove by primary_key: affected rows: %s' % rows)


# self#此处用作测试用
class User(Model):
    # 定义类的属性到列的映射
    __table__ = 'users'
    id = IntegerField('id', True)
    name = StringField('username')
    email = StringField('email')
    password = StringField('password')

    # 这里我定义了一个测试函数，发现在modelMateclass，参数attrs果然出现了这个函数的代号
    def test():
        pass


if __name__ == '__main__':
    ut = User(id=1235, name='Richael', email='mytest@orm.org', password='passmy')
    test = 'mytest';



# User类现在就可以通过类方法实现主键查找：
# user = yield from User.find('123')
# 
# 这样，就可以把一个User实例存入数据库：
# user = User(id=123, name='Michael')
# yield from user.save()
