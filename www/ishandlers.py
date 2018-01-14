# _*_coding:utf-8_*_

__author__ = 'Master Wang'

import re, time, json, hashlib, base64, asyncio

import markdown2

from aiohttp import web

from coroweb import get, post
from apis import Page, APIError, APIPermissionError, APIValueError, APIResourceNotFoundError

from models import User, Comment, Blog, next_id
from config import configs

# 引入数据处理引擎
from dataengine import codeen
# self#
# 程序中用到了深度复制，这里引进相应模块
from copy import deepcopy

# self#
# 为方便分步测试，这里直接引入数据库操纵语句。
from orm import select

# 为自定义的模块添加搜索路径
import sys

sysFc = 'D:\\python_learn\\sysFc'
sys.path.append(sysFc)

from logSf10 import crLog

logger = crLog(fname='D:\桌面\exCodOut.log')
# logger = crLog(fname = 'D:\桌面\handlers.log')
logger.info('Succeed')


@get('/js/{js}')
def isindexJs(js):
    return {'__template__': 'js/' + js}


"""
@get('/css/{css}')
def isindexCss(css):
    return {'__template__': 'css/' + css}
"""

@get('/tt')
def isindexTtt():
    result = [[{'flid': 0, 'line': '<span style="color:red">查询参数错误: </span> '}]]
    return {'__template__': 'ZenCss@@Bk.html', 'fmates': result}

@get('/t')
def isindexTt():
    result = [[{'flid': 0, 'line': '<span style="color:red">查询参数错误: </span> '}]]
    # return {'__template__': 'isearchForm@Tt.html', 'fmates': result}
    # return {'__template__': 'ZenCss@@Bk.html', 'fmates': result}
    return {'__template__': 'ZenCss@Research.html', 'fmates': result}


@get('/x')
def isindexX(**kw):
    try:
        keyword = kw['keyword']
        # 计划 添加<分词>函数# 返回分词结果为keyWords,是一个list
        keyWords = [keyword]
        # keyword 将用于拼接SQL查询语句，执行可靠的检查是必要的(不知道是否应当加上数据库特殊字符的检测，防止SQL注入)
        if len(keyword) == 0 or not isinstance(keyword, str):
            raise ValueError('{{keyword}} 将用于拼接SQL查询语句，执行可靠的检查是必要的')
        result = yield from codeen(keyword)
    # except Exception as e:
    except:
        logger.exception('Break on function isindexX:\n')
        logger.warn(str(kw) + ' |==|  in isindexX(**kw)')
        keyWords = ['']
        result = [[{'flid': 0, 'line': '查询参数错误:  ' + str(kw)}]]
    return {'__template__': 'isearchForm@xi.html',  # 'fmates': alldb,
            'fmates': result,
            'keywords': keyWords}


@get('/ix')
def isindexIX():
    result = yield from codeen('lendwork')
    return {'__template__': 'isearchForm@@ix.html',  # 'fmates': alldb,
            'fmates': result}


@get('/is')
def isindexI():
    return {'__template__': 'isearch@i.html'}


@get('/iiis')
def isindexrIII():
    # alldb = yield from select('show databases', '')
    alldb = yield from select('select * from fmate_code', '', database='fortest')
    logger.info(str(alldb[:10]))
    # for ai in alldb:
    return {'__template__': 'isearch@iii.html', 'fmates': alldb,
            'testtmp': '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'}


@get('/ivs')
def isindexIV():
    # alldb = yield from select('show databases', '')
    alldb = yield from select('select * from fmate_code', '', database='fortest')
    logger.info(str(alldb[:10]))
    # for ai in alldb:
    return {'__template__': 'isearchForm@@iv.html', 'fmates': alldb,
            'testtmp': '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'}


if __name__ == '__main__':
    logger.info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>/n为方便分步测试，这里直接引入数据库操纵语句/n/n")
