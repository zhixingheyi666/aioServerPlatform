# _*_coding:utf-8_*_

__author__ = 'Master Wang'

import re, time, json, hashlib, base64, asyncio

import markdown2

from aiohttp import web

from coroweb import get, post
from apis import Page, APIError, APIPermissionError, APIValueError, APIResourceNotFoundError

from modelsI import getClipActionNote, getNotebooksNote, getAccountsDataNote, getSmartFilingInfoNote, getFilingInfoNote, \
setSelectedAccountNote, getTagsNote, submissionDataNote, tableForTest

from modelsI import yanReports

from models import User, Comment, Blog, next_id\
    , UsersNote, UserUrlsNote, DataNote, TableRegisterNote
from config import configs

# 引入数据处理引擎
from dataengine import codeen
# self#
# 程序中用到了深度复制，这里引进相应模块
from copy import deepcopy

# self#
# 为方便分步测试，这里直接引入数据库操纵语句。
from orm import select
import  random

# 为自定义的模块添加搜索路径
import sys

# sysFc = 'D:\\python_learn\\sysFc'
# sys.path.append(sysFc)

from mylog import *

# logger = crLog(fname = 'D:\桌面\handlers.log')
logger.info('Succeed')


def printObj(obj, logText):
    if isinstance(obj, dict):
        keys = list(obj.keys())
        keys.sort()
        message = ""
        for k in keys:
            message = message + str(k) + ":\t" + str(obj[k]) + "\n        "
    else:
        message = obj
    try:
        logger.info("-----|| %s ||-----------------------------" % logText)
        logger.info(message)
        logger.info("-----|| %s ||-----------------------------" % logText)
    except Exception as e:
        logger.info(e)


@post('/MI/exercise/save_many_reports')
def save_many_reports(request, *, name, action, obj={}):
    if name == "UNKNOWN":
        text = "save_many_reports: Please give the obj name..."
        printObj(obj, text)
        rs = "-----|| This is save_many_reports||-----------------------------"
    elif name == "yan_reports":
        if action == "save":
            if isinstance(obj,list) and len(obj) > 1:
                try:
                    args_array=[]
                    for arg_data in obj:
                        if "author" not in arg_data.keys():
                            raise APIValueError
                        elif "title" not in arg_data.keys():
                            raise APIValueError
                        elif "time_string" not in arg_data.keys():
                            raise APIValueError
                        elif "time_stamp" not in arg_data.keys():
                            raise APIValueError
                        elif "page_num" not in arg_data.keys():
                            raise APIValueError
                        else:
                            arg_arg = []
                            arg_arg.append(arg_data["author"])
                            if "content" not in arg_data.keys():
                                arg_arg.append("")
                            else:
                                arg_arg.append(arg_data["content"])
                            arg_arg.append(arg_data["time_string"])
                            arg_arg.append(int(arg_data["page_num"]))
                            arg_arg.append(arg_data["time_string"])
                            # arg_arg.append(arg_data["time_stamp"])
                            arg_arg.append(arg_data["title"])
                            args_array.append(arg_arg)
                    yan_r = yanReports(author=args_array[0][0], title=args_array[0][5], create_time=args_array[0][2], page_num=args_array[0][3], stamp_time=args_array[0][4], content=args_array[0][1] )
                    text = yield from yan_r.save_many(args_array)
                    rs = "-----|| This is save_many_reports||-----------------------------" + text
                except Exception as e:
                    text = "save_many_reports Failed: %s" % str(e)
                    printObj(obj, text)
                    rs = "-----|| This is save_many_reports||-----------------------------" + text
            else:
                text = "save_many_reports Failed: Obj should be Array type and at least one element"
                printObj(obj, text)
                rs = "-----|| This is save_many_reports||-----------------------------" + text
        else:
            text = "save_many_reports Failed: prama action should be 'save'"
            printObj(obj, text)
            rs = "-----|| This is save_many_reports||-----------------------------" + text
    else:
        text = "save_many_reports Failed: No Model for obj --> %s" % name
        printObj(obj, text)
        rs = "-----|| This is save_many_reports||-----------------------------" + text
    return rs


@post('/MI/trackEvent/objHandler')
def miHandJsonObj(request, *, name, instructions, obj={}):
    """
    #这个代码方案测试成功
    haveModels = {"account": User_note}
    name_model = "blog"
    rs = yield from haveModels[name_model].findNumber('count(id)')
    printObj(rs,"for test haveModels!")
    """

    haveModels = {"account": UsersNote
                , "dispatchPromise\\getClipAction": getClipActionNote
                , "dispatchPromise\\getAccountsData": getAccountsDataNote
                , "dispatchPromise\\getSmartFilingInfo": getSmartFilingInfoNote
                , "dispatchPromise\\getFilingInfo": getFilingInfoNote
                , "dispatchPromise\\getNotebooks": getNotebooksNote
                , "dispatchPromise\\getTags": getTagsNote
                , "dispatchPromise\\setSelectedAccount": setSelectedAccountNote
                , "submissionDataMsg":  submissionDataNote
                , "tableForTest":  tableForTest
                , "accountUrls": UserUrlsNote}

    if name == "UNKNOWN":
        text = "SaveObj Failed: Please give the obj name..."
        printObj(obj, text)
        rs = {'getResourceError': True, 'errorMessage': "-----||{}||-----------------------------".format(text)}
    elif name in haveModels.keys():
        if instructions['action'] == "save":
            model = haveModels[name]
            rs = yield from model.saveObj(obj)
        elif instructions['action'] == "get":
            model = haveModels[name]
            rs = yield from model.get_object(order=instructions['order'])
        else:
            text = "HandObj Failed: Unknown action --> %s" % instructions['action']
            printObj(obj, text)
            rs = {'getResourceError': True, 'errorMessage': "-----||{}||-----------------------------".format(text)}
        """
        # objInstance = haveModels[name](**kw)
        # 为临时测试代码
        objInstance = UsersNote(path="account.email.work@v"+str(random.randint(0, 100000)), mate="email",
                                mate_hash=hashlib.sha1("account.word".encode("utf-8")).digest(), mate_order=10,
                                order=12, mate_format="String", data="None")
        """
        """
        for row in rs:
            objInstance = UsersNote(path=row[0], mate=row[2],
                                mate_hash=row[4], mate_order=row[5],
                                order=row[6], mate_format=row[1], data=row[3])
            yield from objInstance.save()
        """
    else:
        text = "HandObj Failed: No Model for obj --> %s" % name
        printObj(obj, text)
        rs = {'getResourceError': True, 'errorMessage': "-----||{}||-----------------------------".format(text)}
    return rs


@post('/MI/trackEvent')
def miTrackEvent(**kw):
    text = "This is miTrackEvent"
    # printObj(kw, text)
    return "-----|| %s ||-----------------------------" % text


@get('/js/{js}')
def isindexJs(js):
    return {'__template__': 'js/' + js}


"""
@get('/ajax/libs/jquery/1.8.2/{js}')
def isindexJs(js):
    logger.info("=================== "+js+" =================")
    return {'__template__': 'static/' + js}
"""

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
            'fmates': result, 'keywords': keyWords}


"""
#旧版本函数，已过时
@get('/ix')
def isindexIX():
    result = yield from codeen('lendwork')
    return {'__template__': 'isearchForm@@ix.html',  # 'fmates': alldb,
            'fmates': result}

@get('/is')
def isindexI():
    return {'__template__': 'isearch@i.html'}
"""


@get('/iiis')
def isindexrIII():
    # alldb = yield from select('show databases', '')
    alldb = yield from select('SELECT * FROM fmate_code', '', database='fortest')
    logger.info(str(alldb[:10]))
    # for ai in alldb:
    return {'__template__': 'isearch@iii.html', 'fmates': alldb,
            'testtmp': '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'}


@get('/ivs')
def isindexIV():
    # alldb = yield from select('show databases', '')
    alldb = yield from select('SELECT * FROM fmate_code', '', database='fortest')
    logger.info(str(alldb[:10]))
    # for ai in alldb:
    return {'__template__': 'isearchForm@@iv.html', 'fmates': alldb,
            'testtmp': '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'}



if __name__ == '__main__':
    logger.info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>/n为方便分步测试，这里直接引入数据库操纵语句/n/n")

    """
    #下面测试语句失败，因为没有loop
    have_models = {"user":User,"blog":Blog}
    name_model = "blog"
    def test():
        if '__poollist'not in locals() or '__poollist'not in globals():
            # 测试isearch,临时添加生成 链接到fortest数据库的连接池 的语句
            yield from orm.create_pool(loop=loop, host='127.0.0.1', port=3306, user='isearch', password='isearch',
                               database='fortest')
        rs = yield from have_models[name_model].findNumber('count(id)')
        return rs
    test()
    """
