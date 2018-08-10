# coding: utf-8

__author__ = 'Master Wang'

"""
async web application
"""

import asyncio, os, json, time, sys
from datetime import datetime

from aiohttp import web
from jinja2 import Environment, FileSystemLoader

# 为自定义的模块添加搜索路径
"""
    下面这段代码要求自定义模块文件夹，也即sysFc，与本文件(app.py)的父目录在同一文件夹下面
"""
# 本句 os.path.realpath( sys.argv[0] ) 获取本文件所在的实际完整路径，然后分割取第一部分，去除文件名，仅留下路径
ScriptPath = os.path.split( os.path.realpath( sys.argv[0] ) )[0]
# 本句根据前面的路径获取父路径的父路径(也就是sysFc的父路径)
ScriptPath = os.path.abspath(os.path.join(ScriptPath,".."))
# 本句组合得到sysFc路径，也就是自定义模块所在的路径
sysFuncPath = os.path.abspath(os.path.join(ScriptPath,"sysFc"))
sys.path.append(sysFuncPath)

from config import configs
from mylog import *

import orm
from coroweb import add_routes, add_static

from handlers import cookie2user, COOKIE_NAME

# self#测试用临时添加语句
import ipdb
from IPython import embed


# from logSf10 import crLog

# logger = crLog( fname= os.path.abspath(os.path.join(ScriptPath,"exCodOut.log")) )
# logger.info('Succeed defination logger')


def init_jinjia2(app, **kw):
    logger.info('init jinjia2...')
    options = dict(autoescape=kw.get('autoescape', True), block_start_string=kw.get('block_start_string', '{%'),
        block_end_string=kw.get('block_end_string', '%}'), variable_start_string=kw.get('variable_start_string', '{{'),
        variable_end_string=kw.get('variable_end_string', '}}'), auto_reload=kw.get('auto_reload', True))
    path = kw.get('path', None)
    # self#
    """
    path是可以用参数设置的，如果参数没有设定，就按下面代码获取默认模板路径
    """
    if path is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    logger.info('Set jinjia2 template path: %s' % path)
    env = Environment(loader=FileSystemLoader(path), **options)
    filters = kw.get('filters', None)
    if filters is not None:
        for name, f in filters.items():
            env.filters[name] = f
    app['__templating__'] = env


@asyncio.coroutine
def logger_factory(app, handler):
    # 梗#这里不是decorator的用法，但这里也返回了一个函数。
    """
    疑问：app, handler参数在函数中并没有什么用处呀？
    这里的形参request,应该是如下方式传入
    logger_factory(app, handler)(request)
    也就是调用logger_factory，返回值是函数loggerI
    然后调用loggerI(request)
    这里的做法跟装饰器的完全一样，只不过decorator通过@语法，可以一处定义，多处应用，不必每次像下面一样重新定义函数。
    """

    @asyncio.coroutine
    def loggerI(request):
        # logger.info('Request: %s %s' % (request.method, request.path))
        # yield from asyncio.sleep(0.3)
        return (yield from handler(request))

    return loggerI


@asyncio.coroutine
def auth_factory(app, handler):
    @asyncio.coroutine
    def auth(request):
        # logger.info('Check user: %s %s' % (request.method, request.path))
        request.__user__ = None
        cookie_str = request.cookies.get(COOKIE_NAME)
        if cookie_str:
            user = yield from cookie2user(cookie_str)
            if user:
                logger.info('Set current user: %s' % user.email)
                request.__user__ = user
        if request.path.startswith('/manage') and (request.__user__ is None or not request.__user__.admin):
            return web.HTTPFound('/signin')
        return (yield from handler(request))

    return auth


@asyncio.coroutine
def data_factory(app, handler):
    @asyncio.coroutine
    def parse_data(request):
        if request.method == 'POST':
            if request.content_type.startswith('application/json'):
                request.__data__ = yield from request.json()
                logger.info('request json:{}'.format(str(request.__data__)))
            elif request.content_type.startswith('application/x-www-form-urlencoded'):
                request.__data__ = yield from request.post()
                logger.info('request json:{}'.format(str(request.__data__)))
        return (yield from handler(request))

    return parse_data


@asyncio.coroutine
def response_factory(app, handler):
    @asyncio.coroutine
    def response(request):
        # ipdb.set_trace()
        # logger.info('Respone handler...--> respone_factory')
        rr = yield from handler(request)
        if isinstance(rr, web.StreamResponse):
            return rr
        if isinstance(rr, bytes):
            resp = web.Response(body=rr)
            resp.content_type = 'application/octet-stream'
            return resp
        if isinstance(rr, str):
            if rr.startswith('redirect:'):
                return web.HTTPFound(rr[9:])
            resp = web.Response(body=rr.encode('utf-8'))
            resp.content_type = 'text/html;charset=utf-8'
            return resp
        if isinstance(rr, dict):
            template = rr.get('__template__')
            if template is None:
                resp = web.Response(
                    body=json.dumps(rr, ensure_ascii=False, default=lambda o: o.__dict__).encode('utf-8'))
                resp.content_type = 'application/json;charset=utf-8'
                return resp
            else:
                rr['__user__'] = request.__user__
                # self#测试用添加代码
                # rr['__user__'] = 'Mytest'
                resp = web.Response(body=app['__templating__'].get_template(template).render(**rr).encode('utf-8'))
                resp.content_type = 'text/html;charset=utf-8'
                return resp
        # if isinstance(r, int) and t >= 100 and t < 600:
        #    return web.Response(t)
        if isinstance(rr, tuple) and len(rr) == 2:
            t, m = rr
            if isinstance(rr, int) and t >= 100 and t < 600:
                return web.Response(t, str(m))
        # defualt
        resp = web.Response(body=str(rr).encode('utf-8'))
        resp.content_type = 'text/plain;charset=utf-8'
        return resp

    return response


# 时间处理器
def datetime_filter(t):
    delta = int(time.time() - t)
    if delta < 60:
        return u'1分钟前'
    if delta < 3600:
        return u'%s分钟前' % (delta // 60)
    if delta < 86400:
        return u'%s小时前' % (delta // 3600)
    if delta < 604800:
        return u'%s天前' % (delta // 86400)
    dt = datetime.fromtimestamp(t)
    return u'%s年%s月%s日' % (dt.year, dt.month, dt.day)




@asyncio.coroutine
def init(loop):
    # 测试下能不能在同一回环地址如(127.0.0.1),同一端口，同时建立两个连接池。
    # 测试成功！！能在同一回环地址如(127.0.0.1),同一端口，同时建立两个不同的连接池。
    yield from orm.create_pool(loop=loop, host='127.0.0.1', port=3306, user='www-data', password='www-data',
                                database='excodout')

    # self#
    # 测试isearch,临时添加生成 链接到fortest数据库的连接池 的语句
    yield from orm.create_pool(loop=loop, host='127.0.0.1', port=3306, user='isearch', password='isearch',
                               database='fortest')
    # 梗#了解下 middlewares
    app = web.Application(loop=loop, middlewares=[logger_factory, auth_factory, response_factory])

    # self#
    # init_jinjia2(app, filters=dict(datetime=datetime_filter))
    # isearch@i【调试】临时传入【jinja2】 template模板的临时路径
    # init_jinjia2(app, path="D:\\Pycharm\\bootstrap_ln\\practice", filters=dict(datetime=datetime_filter))
    tempPath = os.path.abspath(os.path.join(ScriptPath, "practice"))
    init_jinjia2(app, path=tempPath, filters=dict(datetime=datetime_filter))

    # add_routes第二个参数是模块名，把模块中所有函数处理后添加给app
    add_routes(app, 'handlers')

    # # 迭代开发，更改原app的html文件的路径，故在handlersI中更改原handlers中的路径参数，
    # # add_routes(app, 'handlersI')

    # isearch@i【调试】通过ishandlers给app添加临时路径
    add_routes(app, 'ishandlers')
    add_static(app)

    host = ['127.0.0.1']
    hostI = ['192.168.0.104', '127.0.0.1']
    hostII = ['192.168.0.106', '127.0.0.1']
    # srv = yield from loop.create_server(app.make_handler(), host, 9999)
    # srv = yield from loop.create_server(app.make_handler(), host, 80)
    srv = yield from loop.create_server(app.make_handler(), '127.0.0.1', 9999)
    logger.info('Server started at http://127.0.0.1:9999...')
    return srv


loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()
