## 关于Tornado



#### 回顾Django框架

​	以Django为代表打Python web应用部署时采用wsgi协议与服务器对接（被服务器托管），而这类服务器通常都是基于多线程的，也就是说每一个网络请求服务器都会有一个对应的线程来处理web应用。



#### 考虑两类应用场景

- 用户量大、高并发

  如：秒杀抢购，双十一购物、春节抢火车票

- 大量的HTTP持久连接

  使用同一个TCP连接来发送和接受多个HTTP请求/应答，而不是为每一个新的请求/应答打开新的连接方法

  对于HTTP1.0,可以在请求头中添加Connection：Keep-Alive

  对于HTTP1.1, 所有的连接默认都是持久化连接

  对于这两种场景，通常基于多线程的服务器很难应对。

#### C10K问题

​	对于前文提出的这种高并发问题，我们通常用C10K这一概念来描述，C10K —— Concurrently handing  ten thousand connections，即并发10000个连接， 对于单台服务器而言，根本无法承担，而采用多台服务器分布式又意味着高昂的成本。如何解决C10K问题？



#### Tornado

Tornado在涉及之初就考虑到了性能因素，旨在解决C10K问题，这样的设计使得其称为了一个拥有非常高性能的解决方案（服务器与框架的集合体）；Tornado全称Tornado Web Server，是一个用Python语言写成Web服务器兼Web应用框架，后被Facebook收购，后在2009年9月开源给大众

- 特点：

  ```
  1、轻量级web框架，类似于web.py 拥有异步非阻塞IO的处理方式
  2、拥有出色的抗负载能力，官方用nginx反向代理的方式部署Tornado和其他Python web应用框架进行对比，结果最大浏览量超过第二名近40%
  ```

- 性能：Tornado有着优异的性能。它试图解决C10K问题，即处理大于或等于一万的并发，下表是和一些其他web框架与服务器的对比

```
Tornado 框架和服务器一起组成一个WSGI的全栈替代品。单独在WSGI容器中使用tornado网络框架或者tornado http服务器，有一定的局限性，为了最大化的利用tornado的性能，推荐同时使用tornado网络框架和http服务器
```



#### Tornado 与 Django

- Django

  ```
  Django是走大而全的方向，注重的是高效开发，它最出名的是全自动化的管理后台：只需要ORM，做简单的对象定义，自动生成数据库结构...
  Django提供的方便的ORM,也意味着内置的ORM框架内的其他模块耦合程度高
  
  1、session功能
  2、后台管理
  3、ORM
  ```

- Tornado

  ```
  走的是少而精方向，注重的是性能优越，它最出名的是异步非阻塞的设计方式
  
  1、HTTP服务器
  2、异步编程
  3、WebSocket
  ```



#### 安装和使用

- 安装

  ```
  pip install tornado
  ```

- 第一个Tornado程序

  ```python
  # -*- encoding=utf8 -*-
  import  tornado.web  # 核心文件
  import tornado.ioloop
  
  # 3、主页处理类
  class IndexHandler(tornado.web.RequestHandler):
  
      #处理get请求
      def get(self):
          self.write("Hello world!")
  
  if __name__ == '__main__':
      # 类似于beego的实现方式
      # 1、Application类中填入了路由，和处理函数，相当于MVC中的控制器
      app = tornado.web.Application([(r"/",IndexHandler)])
      # 2、绑定监听端口
      app.listen(8000)
      # 4、ioloop是一个模块，IOLoop是循环类，current函数会判断当前是否有唯一线程启动，没有就创建，start会启动服务器
      tornado.ioloop.IOLoop.current().start()
  ```

  讲解：

  - RequestHandler :

    ​		封装了对应一个请求的所有信息和方法，write(响应信息)就是写响应信息的一个方法；对应每一种http请求方式（get、post等），把对应的处理逻辑写进同名的成员中（对应get请求方式，就写对应的处理逻辑写在get函数中）当没有对应的请求方法时，会返回405报错信息

  - tornado.ioloop:

    ​		tornado的核心io循环模块，封装了Linux的epoll (IO多路复用，系统级别的一种网络连接代理) 和BSD的kqueue，tornado的高性能的基石。以Linux的epoll为例，原理如下：

    ![1570370847503](C:\Users\wanglixing\AppData\Roaming\Typora\typora-user-images\1570370847503.png)

  ```
  在epoll中根据不同的请求传入不同的socket对象，包含着请求的信息等数据，然后在epoll容器中不断的监听其中的socket对象，是否IO阻塞，如果是则跳过，直到非阻塞执行，处理完的请求会被删除
  ```

  

#### Tornado web应用的结构

​		通常一个Tornado web应用包括一个或者多个 [`RequestHandler`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.RequestHandler) 子类, 一个可以将收到的请求路由到对应handler的 [`Application`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.Application) 对象,和 一个启动服务的 `main()` 函数.

一个最小的”hello world”例子就像下面这样:

```
import tornado.ioloop
import tornado.web

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
```



#### `Application` 对象

​		[`Application`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.Application) 对象是负责全局配置的, 包括映射请求转发给处理程序的路由表。路由表是 [`URLSpec`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.URLSpec) 对象(或元组)的列表, 其中每个都包含(至少)一个正则表达式和一个处理类. 顺序问题; 第一个匹配的规则会被使用. 如果正则表达 式包含捕获组, 这些组会被作为 *路径参数* 传递给处理函数的HTTP方法. 如果一个字典作为 [`URLSpec`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.URLSpec) 的第三个参数被传递, 它会作为 *初始参数* 传递给 [`RequestHandler.initialize`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.RequestHandler.initialize)(进行初始化）. 最后 [`URLSpec`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.URLSpec) 可能有一个名字 , 这将允许它被 [`RequestHandler.reverse_url`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.RequestHandler.reverse_url) （做反向解析时使用）.

```python
import tornado.web  # tornado的基础web框架
import tornado.ioloop  # tornado 的核心IO循环模块，封装了Linux的epoll模块，高性能基础
import tornado.httpserver
import tornado.options

from tornado.options import define,options  # 导入定义操作函数
from tornado.web  import RequestHandler,url  # 导入请求接口，和路由函数

# options 是可以全局定义一些变量，以便于全局调用options.port,这里定义了一个port
tornado.options.define("port",type=int,default=8000,help="服务器端口")

#主页处理逻辑，相当于视图
class IndexHandler(RequestHandler):

    def get(self):
        self.write('<a href="'+self.reverse_url("cpp_url") + '">cpp</a>')

class SubjectHandler(RequestHandler):
    #处理逻辑的初始化，这里通过对initialize函数，对接受的参数进行整理操作
    def initialize(self,subject):
        self.subject = subject

    def get(self):
        self.write(self.subject)

if __name__ == "__main__":
    tornado.options.parse_command_line()

    # 实例化一个app，Application：是tornado web框架核心，是与服务器的接口
    app = tornado.web.Application(
        [
            (r"/",IndexHandler),
            # 给视图类传递参数
            (r"/Python",SubjectHandler,{"subject":"python"}),
            # 使用url，并起别名来传递参数，以便于反向解析路由地址
            url(r"/cpp",SubjectHandler,{"subject":"cpp"},name="cpp_url")
        ],
        debug=True
    )

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()
```

例如, 在这个片段中根URL `/` 映射到了 `MainHandler` , 像 `/story/` 后跟着一个数字这种形式的URL被映射到了 `StoryHandler`. 这个数字被传递(作为字符串)给 `StoryHandler.get`.

```
class MainHandler(RequestHandler):
    def get(self):
        self.write('<a href="%s">link to story 1</a>' %
                   self.reverse_url("story", "1"))

class StoryHandler(RequestHandler):
    def initialize(self, db):
        self.db = db

    def get(self, story_id):
        self.write("this is story %s" % story_id)

app = Application([
    url(r"/", MainHandler),
    url(r"/story/([0-9]+)", StoryHandler, dict(db=db), name="story")
    ])
```

​		[`Application`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.Application) 构造函数有很多关键字参数可以用于自定义应用程序的行为 和使用某些特性(或者功能); 完整列表请查看 [`Application.settings`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.Application.settings) .



#### `RequestHandler` 子类

​		Tornado web 应用程序的大部分工作是在 [`RequestHandler`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.RequestHandler) 子类下完成的. 处理子类的主入口点是一个命名为处理HTTP方法的函数: `get()`, `post()`, 等等. 每个处理程序可以定义一个或者多个这种方法来处理不同 的HTTP动作. 如上所述, 这些方法将被匹配路由规则的捕获组对应的参数调用.

在处理程序中, 调用方法如 [`RequestHandler.render`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.RequestHandler.render) 或者 [`RequestHandler.write`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.RequestHandler.write) 产生一个响应. `render()` 通过名字加载一个 [`Template`](https://tornado-zh.readthedocs.io/zh/latest/template.html#tornado.template.Template) 并使用给定的参数渲染它（render就是用来渲染的）. `write()` 被用于非模板基础的输 出; 它接受字符串, 字节, 和字典(字典会被编码成JSON).

在 [`RequestHandler`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.RequestHandler) 中的很多方法的设计是为了在子类中复写和在整个应用 中使用. 常用的方法是定义一个 `BaseHandler` 类, 复写一些方法例如 [`write_error`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.RequestHandler.write_error) 和 [`get_current_user`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.RequestHandler.get_current_user) 然后子类继承使用你自己的 `BaseHandler` 而不是 [`RequestHandler`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.RequestHandler) 在你所有具体的处理程序中.



#### 处理输入请求

处理请求的程序(request handler)可以使用 `self.request` 访问代表当 前请求的对象. 通过 [`HTTPServerRequest`](https://tornado-zh.readthedocs.io/zh/latest/httputil.html#tornado.httputil.HTTPServerRequest) 的类定义查看完整的属性列表.

使用HTML表单格式请求的数据会被解析并且可以在一些方法中使用, 例如 [`get_query_argument`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.RequestHandler.get_query_argument) 和 [`get_body_argument`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.RequestHandler.get_body_argument).

```
class MyFormHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('<html><body><form action="/myform" method="POST">'
                   '<input type="text" name="message">'
                   '<input type="submit" value="Submit">'
                   '</form></body></html>')

    def post(self):
        self.set_header("Content-Type", "text/plain")
        self.write("You wrote " + self.get_body_argument("message"))
```

由于HTLM表单编码不确定一个标签的参数是单一值还是一个列表, [`RequestHandler`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.RequestHandler) 有明确的方法来允许应用程序表明是否它期望接收一个列表. 对于列表, 使用 [`get_query_arguments`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.RequestHandler.get_query_arguments) 和 [`get_body_arguments`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.RequestHandler.get_body_arguments) 而不是它们的单数形式.

通过一个表单上传的文件可以使用 `self.request.files`, 它遍历名字(HTML 标签 `<input type="file">` 的name)到一个文件列表. 每个文件都是一个字典的形式 `{"filename":..., "content_type":..., "body":...}`. `files` 对象是当前唯一的如果文件上传是通过一个表单包装 (i.e. a `multipart/form-data` Content-Type); 如果没用这种格式, 原生上传的数据可以调用 `self.request.body` 使用. 默认上传的文件是完全缓存在内存中的; 如果你需要处理占用内存太大的文件 可以看看 [`stream_request_body`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.stream_request_body) 类装饰器.

由于HTML表单编码格式的怪异 (e.g. 在单数和复数参数的含糊不清), Tornado 不会试图统一表单参数和其他输入类型的参数. 特别是, 我们不解析JSON请求体. 应用程序希望使用JSON代替表单编码可以复写 [`prepare`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.RequestHandler.prepare) 来解析它们的请求:

```
def prepare(self):
    if self.request.headers["Content-Type"].startswith("application/json"):
        self.json_args = json.loads(self.request.body)
    else:
        self.json_args = None
```



#### 复写RequestHandler的方法

除了 `get()`/`post()`/等, 在 [`RequestHandler`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.RequestHandler) 中的某些其他方法 被设计成了在必要的时候让子类重写. 在每个请求中, 会发生下面的调用序 列:

1. 在每次请求时生成一个新的 [`RequestHandler`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.RequestHandler) 对象
2. [`initialize()`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.RequestHandler.initialize) 被 [`Application`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.Application) 配置中的初始化 参数被调用. `initialize` 通常应该只保存成员变量传递的参数; 它不可能产生任何输出或者调用方法, 例如 [`send_error`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.RequestHandler.send_error).
3. [`prepare()`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.RequestHandler.prepare) 被调用. 这在你所有处理子类共享的基 类中是最有用的, 无论是使用哪种HTTP方法, `prepare` 都会被调用. `prepare` 可能会产生输出; 如果它调用 [`finish`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.RequestHandler.finish) (或者 `redirect`, 等), 处理会在这里结束.
4. 其中一种HTTP方法被调用: `get()`, `post()`, `put()`, 等. 如果URL的正则表达式包含捕获组, 它们会被作为参数传递给这个方 法.
5. 当请求结束, [`on_finish()`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.RequestHandler.on_finish) 方法被调用. 对于同步 处理程序会在 `get()` (等)后立即返回; 对于异步处理程序,会在调用 [`finish()`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.RequestHandler.finish) 后返回.

所有这样设计被用来复写的方法被记录在了 [`RequestHandler`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.RequestHandler) 的文档中. 其中最常用的一些被复写的方法包括:

- [`write_error`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.RequestHandler.write_error) - 输出对错误页面使用的HTML.
- [`on_connection_close`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.RequestHandler.on_connection_close) - 当客户端断开时被调用; 应用程序可以检测这种情况,并中断后续处理. 注意这不能保证一个关闭 的连接及时被发现.
- [`get_current_user`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.RequestHandler.get_current_user) - 参考 [用户认证](https://tornado-zh.readthedocs.io/zh/latest/guide/security.html#user-authentication)
- [`get_user_locale`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.RequestHandler.get_user_locale) - 返回 [`Locale`](https://tornado-zh.readthedocs.io/zh/latest/locale.html#tornado.locale.Locale) 对象给当前 用户使用
- [`set_default_headers`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.RequestHandler.set_default_headers) - 可以被用来设置额外的响应 头(例如自定义的 `Server` 头)



#### 错误处理

如果一个处理程序抛出一个异常, Tornado会调用 [`RequestHandler.write_error`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.RequestHandler.write_error) 来生成一个错误页. [`tornado.web.HTTPError`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.HTTPError) 可以被用来生成一个指定的状态码; 所有其他的异常 都会返回一个500状态.

默认的错误页面包含一个debug模式下的调用栈和另外一行错误描述 (e.g. “500: Internal Server Error”). 为了创建自定义的错误页面, 复写 [`RequestHandler.write_error`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.RequestHandler.write_error) (可能在一个所有处理程序共享的一个基类里面). 这个方法可能产生输出通常通过一些方法, 例如 [`write`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.RequestHandler.write) 和 [`render`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.RequestHandler.render). 如果错误是由异常引起的, 一个 `exc_info` 将作为一个关键字参数传递(注意这个异常不能保证是 [`sys.exc_info`](https://docs.python.org/3.4/library/sys.html#sys.exc_info) 当前的 异常, 所以 `write_error` 必须使用 e.g. [`traceback.format_exception`](https://docs.python.org/3.4/library/traceback.html#traceback.format_exception) 代替 [`traceback.format_exc`](https://docs.python.org/3.4/library/traceback.html#traceback.format_exc)).

也可以在常规的处理方法中调用 [`set_status`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.RequestHandler.set_status) 代替 `write_error` 返回一个(自定义)响应来生成一个错误页面. 特殊的例外 [`tornado.web.Finish`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.Finish) 在直接返回不方便的情况下能够在不调用 `write_error` 前结束处理程序.

对于404错误, 使用 `default_handler_class` [`Application setting`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.Application.settings). 这个处理程序会复写 [`prepare`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.RequestHandler.prepare) 而不是一个更具体的方法, 例如 `get()` 所以它可以在任何HTTP方法下工作. 它应该会产生如上所说的错误页面: 要么raise 一个 `HTTPError(404)` 要么复写 `write_error`, 或者调用 `self.set_status(404)` 或者在 `prepare()` 中直接生成响应.



#### 重定向

这里有两种主要的方式让你可以在Tornado中重定向请求: [`RequestHandler.redirect`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.RequestHandler.redirect) 和使用 [`RedirectHandler`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.RedirectHandler).

你可以在一个 [`RequestHandler`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.RequestHandler) 的方法中使用 `self.redirect()` 把用 户重定向到其他地方. 还有一个可选参数 `permanent` 你可以使用它来表明这个 重定向被认为是永久的. `permanent` 的默认值是 `False`, 这会生成一个 `302 Found` HTTP响应状态码, 适合类似在用户的 `POST` 请求成功后的重定向. 如果 `permanent` 是true, 会使用 `301 Moved Permanently` HTTP响应, 更适合 e.g. 在SEO友好的方法中把一个页面重定向到一个权威的URL.

[`RedirectHandler`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.RedirectHandler) 让你直接在你 [`Application`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.Application) 路由表中配置. 例如, 配置一个 静态重定向:

```
app = tornado.web.Application([
    url(r"/app", tornado.web.RedirectHandler,
        dict(url="http://itunes.apple.com/my-app-id")),
    ])
```

[`RedirectHandler`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.RedirectHandler) 也支持正则表达式替换. 下面的规则重定向所有以 `/pictures/` 开始的请求用 `/photos/` 前缀代替:

```
app = tornado.web.Application([
    url(r"/photos/(.*)", MyPhotoHandler),
    url(r"/pictures/(.*)", tornado.web.RedirectHandler,
        dict(url=r"/photos/\1")),
    ])
```

不像 [`RequestHandler.redirect`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.RequestHandler.redirect), [`RedirectHandler`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.RedirectHandler) 默认使用永久重定向. 这是因为路由表在运行时不会改变, 而且被认为是永久的. 当在处理程序中发现重定向的时候, 可能是其他可能改变的逻辑的结果. 用 [`RedirectHandler`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.RedirectHandler) 发送临时重定向, 需要添加 `permanent=False` 到 [`RedirectHandler`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.RedirectHandler) 的初始化参数.



#### 异步处理

Tornado默认会同步处理: 当 `get()`/`post()` 方法返回, 请求被认为结束 并且返回响应. 因为当一个处理程序正在运行的时候其他所有请求都被阻塞, 任何需要长时间运行的处理都应该是异步的, 这样它就可以在非阻塞的方式中调用 它的慢操作了. 这个话题更详细的内容包含在 [异步和非阻塞I/O](https://tornado-zh.readthedocs.io/zh/latest/guide/async.html) 中; 这部分是关于在 [`RequestHandler`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.RequestHandler) 子类中的异步技术的细节.

使用 [`coroutine`](https://tornado-zh.readthedocs.io/zh/latest/gen.html#tornado.gen.coroutine) 装饰器是做异步最简单的方式. 这允许你使用 `yield` 关键 字执行非阻塞I/O, 并且直到协程返回才发送响应. 查看 [协程](https://tornado-zh.readthedocs.io/zh/latest/guide/coroutines.html) 了解 更多细节.

在某些情况下, 协程不如回调为主的风格方便, 在这种情况下 [`tornado.web.asynchronous`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.asynchronous) 装饰器可以用来代替. 当使用这个装饰器的时候, 响应不会自动发送; 而请求将一直保持开放直到callback调用 [`RequestHandler.finish`](https://tornado-zh.readthedocs.io/zh/latest/web.html#tornado.web.RequestHandler.finish). 这需要应用程序确保这个方法被调用或者其他用户 的浏览器简单的挂起.

这里是一个使用Tornado’s 内置的 [`AsyncHTTPClient`](https://tornado-zh.readthedocs.io/zh/latest/httpclient.html#tornado.httpclient.AsyncHTTPClient) 调用FriendFeed API的例 子:

```
class MainHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        http = tornado.httpclient.AsyncHTTPClient()
        http.fetch("http://friendfeed-api.com/v2/feed/bret",
                   callback=self.on_response)

    def on_response(self, response):
        if response.error: raise tornado.web.HTTPError(500)
        json = tornado.escape.json_decode(response.body)
        self.write("Fetched " + str(len(json["entries"])) + " entries "
                   "from the FriendFeed API")
        self.finish()
```

当 `get()` 返回, 请求还没有完成. 当HTTP客户端最终调用 `on_response()`, 这个请求仍然是开放的, 通过调用 `self.finish()`, 响应最终刷到客户端.

为了方便对比, 这里有一个使用协程的相同的例子:

```
class MainHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        http = tornado.httpclient.AsyncHTTPClient()
        response = yield http.fetch("http://friendfeed-api.com/v2/feed/bret")
        json = tornado.escape.json_decode(response.body)
        self.write("Fetched " + str(len(json["entries"])) + " entries "
                   "from the FriendFeed API")
```

更多高级异步的示例, 请看 [chat example application](https://github.com/tornadoweb/tornado/tree/stable/demos/chat), 实现了一个 使用 [长轮询(long polling)](http://en.wikipedia.org/wiki/Push_technology#Long_polling) 的AJAX聊天室. 长轮询的可能想要覆盖 `on_connection_close()` 来在客户端关闭连接之后进行清 理(注意看方法的文档来查看警告).