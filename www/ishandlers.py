#_*_coding:utf-8_*_

__author__ = 'Master Wang'

import re, time, json, hashlib, base64, asyncio

import markdown2

from aiohttp import web

from coroweb import get, post
from apis import Page, APIError, APIPermissionError, APIValueError, APIResourceNotFoundError

from models import User, Comment, Blog, next_id
from config import configs

# self#
# 为方便分步测试，这里直接引入数据库操纵语句。
from orm import select

#为自定义的模块添加搜索路径
import sys
sysFc = 'D:\\python_learn\\sysFc'
sys.path.append(sysFc)

from logSf10 import crLog
logger = crLog(fname = 'D:\桌面\exCodOut.log')
#logger = crLog(fname = 'D:\桌面\handlers.log')
logger.info('Succeed')

@get('/is')
def isindexI():
    return {
        '__template__':'isearch@i.html'
    }

@get('/iiis')
def isindexrIII():
    # alldb = yield from select('show databases', '')
    alldb = yield from select('select * from fmate_code', '', database = 'fortest')
    logger.info(str(alldb))
    return {
        '__template__':'isearch@iii.html'
    }
if __name__ == '__main__':
    logger.info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>/n为方便分步测试，这里直接引入数据库操纵语句/n/n")
