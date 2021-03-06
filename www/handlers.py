# coding: utf8

__author__ = 'Master Wang'

'''
url handlers
'''

import re, time, json, hashlib, base64, asyncio

import markdown2

from aiohttp import web

from coroweb import get, post
from apis import Page, APIError, APIPermissionError, APIValueError, APIResourceNotFoundError

from models import User, Comment, Blog, next_id
from config import configs

import ipdb
#为自定义的模块添加搜索路径
import sys
# sysFc = 'D:\\python_learn\\sysFc'
# sys.path.append(sysFc)

from mylog import *

#logger = crLog(fname = 'D:\桌面\handlers.log')
logger.info('Succeed')
#from logSf10 import logger 
#logger = logger


COOKIE_NAME = 'Exsession' 
_COOKIE_KEY = configs.session.secret

def check_admin(request):
     if request.__user__ is None or not request.__user__.admin:
        raise APIPermissionError()

def get_page_index(page_str):
    p = 1
    try:
        p = int(page_str)
    except ValueError as e:
        pass
    if p < 1:
        p = 1
    return p

def user2cookie(user, max_age):
    '''
    Generate cookie str by user.
    '''
    #build cookie string by: id-expires-sha1
    expires = str(int(time.time() + max_age))
    s = '%s-%s-%s-%s' % (user.id, user.passwd, expires, _COOKIE_KEY)
    L = [user.id, expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
    return '-'.join(L)

def text2html(text):
    lines = map(lambda s: '<p>%s</p>' % s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'), filter(lambda s: s.strip() != '', text.split('\n')))
    return ''.join(lines)

@asyncio.coroutine
def cookie2user(cookie_str):
    '''
    Parse cookie and load user if cookie is valid
    '''
    if not cookie_str:
        return None
    try:
        L = cookie_str.split('-')
        if len(L) != 3:
            return None
        uid, expires, sha1 = L
        if int(expires) < time.time():
            return None
        user = yield from User.find(uid)
        if user is None:
            return None
        s = '%s-%s-%s-%s' % (user.id, user.passwd, expires, _COOKIE_KEY)
        if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
            logger.info('invalid sha1')
            return None
        user.passwd = '******'
        return user
    except Exception as e:
        logger.exception(e)
        return None

"""
#<test>
@get('/')
def indexI(*, page = '1'):
    # ipdb.set_trace()
    # summary = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'
    blogs = [
        Blog(id='1', name='静静工作了', summary=summary, created_at=time.time()-120),
        Blog(id='2', name='老弟陪我打羽毛球', summary=summary, created_at=time.time()-3600),
        Blog(id='3', name='我的第一个WEB程序', summary=summary, created_at=time.time()-7200),
        Blog(id='9', name='Master Wang', summary=summary, created_at=time.time()-8200)
    ]
    return {
            '__template__':'blogs.html',
            'page':page,
            'blogs':blogs
            }
#</test>
"""


@get('/')
def index(*, page = '1'):
    page_index = get_page_index(page)
    num = yield from Blog.findNumber('count(id)')
    page = Page(num, page_index)
    if num == 0:
        blogs = []
    else:
        # 测试代码临时添加
        # blogs = yield from Blog.findAll(orderBy = 'created_at desc', limit = (page.offset, page.limit))
        blogs = yield from Blog.findAll(orderBy = 'created_at', limit = (page.offset, page.limit))
    return {
            '__template__':'blogs.html',
            'page':page,
            'blogs':blogs
            }
@get('/blog/{id}')
def get_blog(id):
    # 这里blog是Blog的实例，isinstance(blog,Blog)==True,isinstance(blog,dict)===True,issubclass(Blog,dict)==True
    blog = yield from Blog.find(id)
    comments = yield from Comment.findAll('blog_id=?', [id], orderBy = 'created_at desc')
    for c in comments:
        c.html_content = text2html(c.content)
    blog.html_content = markdown2.markdown(blog.content)
    return {
            '__template__': 'blog.html',
            'blog': blog,
            'comments': comments
            }


@get('/image/cover')
def get_cover_image():
    return {
        '__template__': 'cover(1).jpg'
    }

@get('/register')
def register():
    return {
            '__template__': 'register.html'
            }

# 测试临时添加代码
@get('/manage/blogs/signin')
def manage_blogs_signinI():
    return {
        '__template__':'signin.html'
    }

@get('/signin')
def signin():
    return {
            '__template__':'signin.html'
            }

@post('/api/authenticate')
def authenicate(*, email, passwd):
    if not email:
        raise APIValueError('email', 'Invalid email.')
    if not passwd:
        raise APIValueError('passwd', 'Invalid passwd.')
    user = yield from User.findAll('email=?', [email])
    if len(user) == 0:
        raise APIValueError('email', 'Email not exist.')
    user = user[0]
    #check password
    sha1 = hashlib.sha1()
    sha1.update(user.id.encode('utf-8'))
    sha1.update(b':')
    sha1.update(passwd.encode('utf-8'))
    if user.passwd != sha1.hexdigest():
        raise APIValueError('passwd', 'Invalid passwd.')
    #authenicate ok, set cookie:
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user,86400), max_age = 86400, httponly = True)
    user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii = False).encode('utf-8')
    return r

@get('/signout')
def signout(request):
    referer = request.headers.get('Referer')
    r = web.HTTPFound(referer or '/')
    r.set_cookie(COOKIE_NAME, '-deleted-', max_age = 0, httponly = True)
    logger.info('User signed out.')

@get('/manage/')
def manage():
    return 'redirect:/manage/comments'

@get('/manage/comments')
def manage_comments(*, page = '1'):
    return {
            '__template__': 'manage_comments.html',
            'page_index': get_page_index(page)
            }


@get('/manage/blogs')
def manage_blogs(*, page = '1'):
    return {
            '__template__':'manage_blogs.html',
            'page_index':get_page_index(page)
            }

@get('/manage/blogs/create')
def manage_create_blog():
    return {
            '__template__':'manage_blog_edit.html',
            'id': '',
            'action': '/api/blogs'
            }

@get('/manage/blogs/edit')
def manage_edit_blog(*, id):
    return {
            '__template__':'manage_blog_edit.html',
            'id': id,
            'action': '/api/blogs/%s' % id
            }

@get('/manage/users')
def manage_users(*, page = '1'):
    return {
            '__template__':'manage_users.html',
            'page_index':get_page_index(page)
            }
    
@get('/api/comments')
def api_comments(*, page = '1'):
    page_index = get_page_index(page)
    num = yield from Comment.findNumber('count(id)')
    p = Page(num, page_index)
    if num == 0:
        return dict(page = p, comment = ())
    comments = yield from Comment.findAll(orderBy = 'created_at desc', limit = (p.offset, p.limit))
    return dict(page = p, comments = comments)
    
@post('/api/blogs/{id}/comments')
def api_create_comment(id, request, *, content):
    user = request.__user__
    if user is None: 
        raise APIPermissionError('Please sign in frist.')
    if not content and content.strip():
        raise APIValueError('content')
    blog = yield from Blog.find(id)
    if blog is None: 
        raise APIResourceNotFoundError('blog')
    comment = Comment(blog_id = blog.id, user_id = user.id, user_name = user.name, user_image = user.image, content = content.strip())
    yield from comment.save()
    return comment
@post('/api/comments/{id}/delete')
def api_delete_comment(id, request):
    check_admin(request)
    c = yield from Comment.find(id)
    if c is None:
        raise APIResourceNotFoundError('comment')
    yield from c.remove()
    return dict(id = id)


@get('/api/users')
def api_get_users(*, page = '1'):
    page_index = get_page_index(page)
    num = yield from User.findNumber('count(id)')
    p = Page(num, page_index)
    if num == 0:
        return dict(page = p, users = ())
    users = yield from User.findAll(orderBy = 'created_at desc', limit = (p.offset, p.limit))
    for u in users:
        u.passwd = '******'
    return dict(page = p, users = users)

_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')

@post('/api/users')
def api_register_user(*, email, name, passwd):
    if not name and not name.strip():
        raise APIValueError('name')
    if not email and not _RE_EMAIL.match(email):
        raise APIValueError('email')
    if not passwd and not _RE_SHA1.match(passwd):
        raise APIValueError('passwd')
    users = yield from User.findAll('email=?', [email])
    if len(users) > 0:
        raise APIError('register:failed', 'email', 'Email is already in use.')
    uid = next_id()
    sha1_passwd = '%s:%s' % (uid, passwd)
    user = User(id = uid,  name = name.strip(), email = email, passwd = hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(), image='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(email.encode('utf-8')).hexdigest())
    yield from user.save()
    #make session cookie:
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user,86400), max_age = 86400, httponly = True)
    user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii = False).encode('utf-8')
    return r
    
@get('/api/blogs')
def api_blogs(*, page = '1'):
    page_index = get_page_index(page)
    num = yield from Blog.findNumber('count(id)')
    p = Page(num, page_index)
    if num == 0:
        return dict(page = p, blogs = ())
    blogs = yield from Blog.findAll(orderBy = 'created_at desc', limit = (p.offset, p.limit))
    return dict(page = p, blogs = blogs)

@get('/api/blogs/{id}')
def api_get_blog(*, id):
    blog = yield from Blog.find(id)
    return blog


@post('/api/blogs')
def api_create_blog(request, *, name, summary, content):
    check_admin(request)
    if not name and not name.strip():
        raise APIValueError('name', 'name cannot be empty.')
    if not summary and not summary.strip():
        raise APIValueError('summary', 'summary annot be empty.')
    if not content and not content.strip():
        raise APIValueError('content', 'content annot be empty.')
    blog = Blog(user_id = request.__user__.id, user_name = request.__user__.name,  user_image = request.__user__.image, name  = name.strip(), summary = summary.strip(), content = content.strip())
    yield from blog.save()
    return blog 

@post('/api/blogs/{id}')
def api_update_blog(id, request, *, name, summary, content):
    check_admin(request)
    blog = yield from Blog.find(id)
    if not name and not name.strip():
        raise APIValueError('name', 'name cannot be empty.')
    if not summary and not summary.strip():
        raise APIValueError('summary', 'summary annot be empty.')
    if not content and not content.strip():
        raise APIValueError('content', 'content annot be empty.')
    blog.name = name.strip()
    blog.summary = summary.strip()
    blog.content = content.strip()
    yield from blog.update()
    return blog
    
@post('/api/blogs/{id}/delete')
def api_delete_blog(request, *, id):
    check_admin(request)
    blog = yield from Blog.find(id)
    yield from blog.remove()
    return dict(id = id) 
