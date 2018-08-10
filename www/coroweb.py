# coding: utf-8

__author__ = 'Master Wang'


import sys, ipdb

from mylog import *
import json
# logger = crLog(fname = 'D:\桌面\coroweb.log')
# from logSf10 import logger
# logger = logger


import asyncio, os, inspect, functools

from urllib import parse
from aiohttp import web
from apis import APIError



def get(path):
    '''
    Define decorator @get('path')
    '''

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)

        wrapper.__method__ = 'GET'
        wrapper.__route__ = path
        return wrapper

    return decorator


def post(path):
    '''
    Define decorator @post('/path')
    '''

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)

        wrapper.__method__ = 'POST'
        wrapper.__route__ = path
        return wrapper

    return decorator
"""
根据度娘搜到的，inspect模块主要提供了四种用处：
(1). 对是否是模块，框架，函数等进行类型检查。
(2). 获取源码
(3). 获取类或函数的参数的信息
(4). 解析堆栈
    下面记录一下：获取类或函数的参数的信息
    inspect.signature（fn)将返回一个inspect.Signature类型的对象，值为fn这个函数的所有参数
    inspect.Signature.parameters是一个mappingproxy（映射）类型的对象，值为一个有序字典（Orderdict)。
    这个字典里的key是函数的参数名，这个字典里的value是一个inspect.Parameter类型的对象(我们暂时称其为
    param_obj)，根据我的理解，这个param_obj对象里包含的一个参数的各种信息，而其中：
    ·param_obj.kind的属性值表示这个参数是何种类型的参数
        与廖雪峰讲义(廖雪峰的讲法不是很科学，仅供参考)中的名称的对应关系如下：
        POSITIONAL_OR_KEYWORD：在可变参数(VAR_POSITIONAL)之前的其kind属性都是这个值，包括有默认值和没有默认值的
        VAR_POSITIONAL：定义函数时候，带一个*号的参数，廖雪峰称之为可变参数
        KEYWORD_ONLY：廖雪峰称之为命名关键字参数，实则在VAR_POSITIONAL后面的参数就是KEYWORD参数。
                        KEYWORD_ONLY参数必须正确的传入参数的名字，而POSITIONAL_OR_KEYWORD仅需要
                        传入参数值即可。KEYWORD_ONLY有默认值和没有默认值都可。
        VAR_KEYWORD；在定义参数时候位置在最后，带两个*号的参数，廖雪峰把这个和KEYWORD_ONLY称之为关键字参数
                        但根据其英文意思，我觉得称之为可变关键字参数比较合适。
        总结来说，我认为python中的参数分可以分为两大类，一类是只传递值的，包括POSITIONAL_OR_KEYWORD和POSITIONAL_OR_KEYWORD
            另一类是传递映射对的，就是传递名字和值的，包括POSITIONAL_OR_KEYWORD和POSITIONAL_OR_KEYWORD。              
    ·param_obj.default属性：如果这个参数有默认值，即返回这个默认值，如果没有，返回一个inspect._empty类。
        所以如下语句值为真的时候，即可判定其没有默值
        param.default == inspect.Parameter.empty
    
    参考网址：
    https://blog.csdn.net/weixin_35955795/article/details/53053762
"""

# 提取没有默认值的关键字参数，也即必要，调用函数时候必须要传入值的参数(required)
def get_required_kw_args(fn):
    args = []
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        # 提取没有默认值的关键字参数，也即必要，调用函数时候必须要传入值的参数(required)
        if param.kind == inspect.Parameter.KEYWORD_ONLY and param.default == inspect.Parameter.empty:
            args.append(name)
            return tuple(args)


def get_named_kw_args(fn):
    args = []
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        # 获取所有(命名的,named)关键字参数
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            args.append(name)
    return tuple(args)


# 判断是否存在某一个(命名的,named)关键字参数
def has_named_kw_args(fn):
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            return True


# 判断是否存在可变关键字参数
def has_var_kw_arg(fn):
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.VAR_KEYWORD:
            return True


# 判断是有一个参数的名字叫request
def has_request_arg(fn):
    args = []
    sig = inspect.signature(fn)
    params = sig.parameters
    found = False
    for name, param in params.items():
        if name == 'request':
            found = True
            continue
        if found and (
                    param.kind != inspect.Parameter.VAR_POSITIONAL and param.kind != inspect.Parameter.KEYWORD_ONLY and param.kind != inspect.Parameter.VAR_KEYWORD):
            raise ValueError(
                'request parameter must be the last named parameter in function: %s%s' % (fn.__name__, str(sig)))
    return found


# self# 响应来自客户端的api或者url请求，做些预处理，然后调用传入的事件处理函数fn
class RequestHandler(object):
    # ipdb.set_trace()
    def __init__(self, app, fn):
        self._app = app
        self._func = fn
        self._has_request_arg = has_request_arg(fn)
        self._has_var_kw_arg = has_var_kw_arg(fn)
        self._has_named_kw_args = has_named_kw_args(fn)
        self._named_kw_args = get_named_kw_args(fn)
        self._required_kw_args = get_required_kw_args(fn)


    @asyncio.coroutine
    def __call__(self, request):
        # ipdb.set_trace()
        kw = None
        # 这里写的不妥，因为_has_named_kw_args包含_required_kw_args
        if self._has_var_kw_arg or self._has_named_kw_args or self._required_kw_args:
            if request.method == 'POST':
                if not request.content_type:
                    return web.HTTPBadReqiuest('Missing Content-Type.')
                ct = request.content_type.lower()
                if ct.startswith('application/json'):
                    # params = yield from request.json()
                    params = yield from request.text()
                    try:
                        params = json.loads(params)
                    except Exception as e:
                        logger.info("----------Failed convert to JSON---------------------")
                        pass
                    if not isinstance(params, dict):
                        return web.HTTPBadRequest('JSON body must be object.')
                    kw = params
                elif ct.startswith('application/x-www-form-urlencoded') or ct.startswith('multipart/form-data'):
                    params = yield from request.post()
                    kw = dict(**params)
                else:
                    return web.HTTPBadRequest('Unsupported Content-Type: %s' % request.content_type)
            if request.method == 'GET':
                qs = request.query_string
                if qs:
                    kw = dict()
                    for k, v in parse.parse_qs(qs, True).items():
                        kw[k] = v[0]
        if kw is None:
            kw = dict(**request.match_info)
        else:
            # 这里的逻辑也有问题，正确的意思是，如果有命名关键字参数但是没有可变关键字参数的话，
            # 应该删除预选参数列表中多余的参数，应该是if self._named_kw_args and not self._has_var_kw_arg:
            # not a or b 的结合性：not 的优先级是大于and和or的，所以相当于(not a) or b
            if not self._has_var_kw_arg or self._named_kw_args:
                # remove all unamed kw:
                copy = dict()
                for name in self._named_kw_args:
                    if name in kw:
                        copy[name] = kw[name]
                kw = copy
                # check named arg:
                for k, v in request.match_info.items():
                    if k in kw:
                        logger.warning('Duplicate arg name in named arg and kw args: %s' % k)
                    kw[k] = v
        if self._has_request_arg:
            kw['request'] = request
        # check required kw:
        if self._required_kw_args:
            for name in self._required_kw_args:
                if not name in kw:
                    return web.HTTPBadRequest('Missing argument: %s' % name)
                kw_str = "{\n"
                for k, v in kw.items():
                    kw_str = kw_str + "\t" + str(k)[:30] + "\t\t" + str(v)[:60] + "\n"
                kw_str = kw_str + "}"
                logger.info('call with args: %s' % kw_str)
        try:
            r = yield from self._func(**kw)
            return r
        except APIError as e:
            return dict(error=e.error, data=e.error, message=e.message)


def add_static(app):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    # ipdb.set_trace()
    app.router.add_static('/static/', path)
    logger.info('Add static %s => %s' % ('/static/', path))

    # 调试js和css方便临时添加静态路径
    # pathT = 'D:\\Pycharm\\bootstrap_ln\\practice'
    # app.router.add_static('/practice/', pathT)
    # 本句根据前面的路径获取父路径的父路径(也就是www的父路径)
    tempPath = os.path.abspath(os.path.join(path, "../.."))
    tempPath = os.path.abspath(os.path.join(tempPath, "practice"))
    app.router.add_static('/practice/', tempPath)
    logger.info('Add static %s => %s' % ('/practice/', tempPath))
    # 调试其他网站，临时加的路径
    app.router.add_static('/ajax/libs/jquery/1.8.2/', tempPath)
    logger.info('Add static %s => %s' % ('/ajax/libs/jquery/1.8.2/', tempPath))


def add_route(app, fn):
    method = getattr(fn, '__method__', None)
    path = getattr(fn, '__route__', None)
    if path is None or method is None:
        raise ValueError('@get or @post not defined in %s.' % str(fn))
    if not asyncio.iscoroutinefunction(fn) and not inspect.isgeneratorfunction(fn):
        fn = asyncio.coroutine(fn)
    logger.info(
        'Add route %s %s => %s(%s)' % (method, path, fn.__name__, ','.join(inspect.signature(fn).parameters.keys())))
    app.router.add_route(method, path, RequestHandler(app, fn))


def add_routes(app, module_name):
    # ipdb.set_trace()
    n = module_name.rfind('.')
    if n == (-1):
        mod = __import__(module_name, globals(), locals())
    else:
        name = module_name[n + 1:]
        mod = getattr(__import__(module_name[:n], globals(), locals(), [name]), name)
    for attr in dir(mod):
        if attr.startswith('_'):
            continue
        fn = getattr(mod, attr)
        if callable(fn):
            method = getattr(fn, '__method__', None)
            path = getattr(fn, '__route__', None)
            if method and path:
                add_route(app, fn)
