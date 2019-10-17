## Tornado 的异步使用



Tornado默认是单进程单线程。实时的web特性通常需要为每个用户一个大部分时间都处于空闲的长连接. 在传统的同步web服务器中,这意味着需要给每个用户分配一个专用的线程,这样的开销是十分巨大的。为了减小对于并发连接需要的开销,Tornado使用了一种单线程事件循环的方式. 这意味着所有应用程序代码都应该是异步和非阻塞的,因为在同一时刻只有一个操作是有效的.

Tornado 中推荐用 协程 来编写异步代码. 协程使用 Python 中的关键字 yield 来替代链式回调来实现挂起和继续程序的执行(像在 gevent 中使用的轻量级线程合作的方法有时也称作协程, 但是在 Tornado 中所有协程使用异步函数来实现的明确的上下文切换).



#### 同步阻塞（Blocking）

一个函数通常在它等待返回值的时候被 阻塞 .一个函数被阻塞可能由于很多原因: 网络I/O,磁盘I/O,互斥锁等等.事实上, 每一个 函数都会被阻塞,只是时间会比较短而已, 当一个函数运行时并且占用CPU(举一个极端的例子来说明为什么CPU阻塞的时间必须考虑在内, 考虑以下密码散列函数像bcrypt, 这个函数需要占据几百毫秒的CPU时间, 远远超过了通常对于网络和磁盘请求的时间). 一个函数可以在某些方面阻塞而在其他方面不阻塞.举例来说, tornado.httpclient 在默认设置下将阻塞与DNS解析,但是在其它网络请求时不会阻塞 (为了减轻这种影响,可以用 ThreadedResolver 或通过正确配置 libcurl 使用 tornado.curl_httpclient ). 在Tornado的上下文中我们通常讨论网络I/O上下文阻塞, 虽然各种阻塞已经被最小化了.

```python
#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Python 3.5
import time
import tornado.web
class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('index')
def doing():
    time.sleep(10)
    return 'Blocking'
class BlockingHandler(tornado.web.RequestHandler):
    def get(self):
        result = doing()
        self.write(result)
application = tornado.web.Application([
    (r"/index", IndexHandler),
    (r"/blocking", BlockingHandler),
])
if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
    
```

浏览器访问：http://127.0.0.1:8888/index
浏览器访问：http://127.0.0.1:8888/blocking
你会发现blocking会一直在转圈，处于一个堵塞状态。
你再访问index页面，你发现index页面也会堵塞住。



#### 异步非阻塞（Non Blocking）

一个 异步 函数在它结束前就已经返回了,而且通常会在程序中触发一些动作然后在后台执行一些任务. (和正常的 同步 函数相比, 同步函数在返回之前做完了所有的事). 这里有几种类型的异步接口:

- 回调函数(基本不用)
- tornado协程+生成器
- tornado协程+Future
- 线程池进程池



#### tornado封装的协程+生成器

```
#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Python 3.5
import tornado.web
from tornado import gen

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('index')
        
@gen.coroutine
def doing():
    """
    穿上@gen.coroutine 装饰器之后，最终结果会返回一个可以被yield 的生成器 Future 对象
    与众不同的是这个函数的返回值需要以 raise gen.Return() 这种形式返回。
    :return: Future object
    """
    # time.sleep(10)     # time.sleep() 是blocking 的，不支持异步操作，我刚开始测试tornado的时候坑了
    yield gen.sleep(10)  # 使用这个方法代替上面的方法模拟 I/O 等待的情况, 可以点进去看下这个方法的介绍
    raise gen.Return('Non-Blocking')
    
class NonBlockingHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self):
        result = yield doing()
        self.write(result)
        
application = tornado.web.Application([
    (r"/index", IndexHandler),
    (r"/nonblocking", NonBlockingHandler),
])
if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
    
```

浏览器访问：http://127.0.0.1:8888/nonblocking
浏览器访问：http://127.0.0.1:8888/index
你会发现nonblocking会一直在转圈，处于一个堵塞状态。
你再访问index页面，你发现index页面能够访问不受影响。
包含了 yield 关键字的函数是一个 生成器(generator). 所有的生成器都是异步的; 当调用它们的时候,会返回一个生成器对象,而不是一个执行完的结果. @gen.coroutine 装饰器通过 yield 表达式和生成器进行交流, 而且通过返回一个 Future 与协程的调用方进行交互. 协程一般不会抛出异常: 它们抛出的任何异常将被 Future 捕获 直到它被得到. 这意味着用正确的方式调用协程是重要的, 否则你可能有被 忽略的错误。@gen.coroutine 可以让你的函数以异步协程的形式运行，但是依赖第三方的异步库，要求你的函数本身不是blocking的。例如上面的os.sleep() 方法是blocking 的，没办法实现异步非阻塞。



#### tornado封装的协程+Future

上面提到Future 到底是什么呢，原始的 Future 版本十分复杂, 但是 Futures 是 Tornado 中推荐使用的一种做法, 因为它有两个主要的优势. 错误处理时通过 Future.result 函数可以简单的抛出一个异常 (不同于某些传统的基于回调方式接口的 一对一的错误处理方式), 而且 Futures 对于携程兼容的很好. 我们这里简单使用一下future 写一个异步函数。

```python
#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Python 3.5
import tornado.web
from tornado import gen
from tornado.concurrent import Future

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('index')
        
def doing():
    future = Future()
    # here doing some things ...
    future.set_result('Non-Blocking')
    return future
    
class NonBlockingHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self):
        result = yield doing()
        self.write(result)
        
application = tornado.web.Application([
    (r"/index", IndexHandler),
    (r"/nonblocking", NonBlockingHandler),
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
    
```



#### Python 3.5: async and await

官方还介绍了在另一种写法， Python 3.5 引入了 async 和 await 关键字(使用这些关键字的 函数也被称为”原生协程”). 从Tornado 4.3, 你可以用它们代替 yield 为基础的协程. 只需要简单的使用 async def foo() 在函数定义的时候代替 @gen.coroutine 装饰器, 用 await 代替yield. 本文档的其他部分会继续使用 yield的风格来和旧版本的Python兼容, 但是如果 async 和 await 可用的话，它们运行起来会更快

```python
#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Python 3.5
import tornado.web
from tornado import gen

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('index')
        
async def doing():
    await gen.sleep(10)  # here are doing some things
    return 'Non-Blocking'
    
class NonBlockingHandler(tornado.web.RequestHandler):
    async def get(self):
        result = await doing()
        self.write(result)
        
application = tornado.web.Application([
    (r"/index", IndexHandler),
    (r"/nonblocking", NonBlockingHandler),
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
```



并行执行

```
#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Python 3.5
import tornado.web
from tornado import gen
class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('index')
        
@gen.coroutine
def doing():
    yield gen.sleep(10)
    raise gen.Return('Non-Blocking')
    
class NonBlockingHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self):
        result1, result2 = yield [doing(), doing()]
        self.write(result1)
        
application = tornado.web.Application([
    (r"/index", IndexHandler),
    (r"/nonblocking", NonBlockingHandler),
])
if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
    
```

那async ，await 那种方式能并行执行吗？ 答案也是可以的：

```
#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Python 3.5
# Date: 2017/12/13

import tornado.web
from tornado import gen
class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('index')
        
async def doing():
    await gen.sleep(10)
    return 'Non-Blocking'
    
class NonBlockingHandler(tornado.web.RequestHandler):
    async def get(self):
        result1, result2 = await gen.convert_yielded([doing(), doing()])
        self.write(result1)
        
application = tornado.web.Application([
    (r"/index", IndexHandler),
    (r"/nonblocking", NonBlockingHandler),
])
if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
```

await 关键字比 yield 关键字功能要少一些. 例如,在一个使用 yield 的协程中， 你可以得到Futures 列表, 你也可以使用 tornado.gen.convert_yielded 来把任何使用 yield 工作的代码转换成使用 await 的形式.



#### 线程池

coroutine 是给Non-blocking 函数提供异步协程的方式运行， ThreadPoolExecutor 则可以给blocking 的函数提供异步的方式运行，但是由于是多线程的，Python 使用多线程对性能来说是需要谨慎的，大量的计算量的情况可能会造成性能的下降。

```
#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Python 3.5
import time
import os
import tornado.web
from tornado import gen
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('index')
        self.write('index')
        print('index')
        
class NonBlockingHandler(tornado.web.RequestHandler):
    executor = ThreadPoolExecutor(4)
    @gen.coroutine
    def get(self):
        result = yield self.doing()
        self.write(result)
        print(result)
    # 使用tornado 线程池不需要加上下面的装饰器到I/O函数
    @run_on_executor
    def doing(self):
        # time.sleep(10)
        # yield gen.sleep(10)
        os.system("ping -c 20 www.baidu.com")  # 模拟I/O 任务
        return 'Non-Blocking'
        
application = tornado.web.Application([
    (r"/index", IndexHandler),
    (r"/nonblocking", NonBlockingHandler),
])
if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
```

设置超时时间

```
#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Python 3.5
import time
import datetime
import os
import tornado.web
from tornado import gen
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('index')
        print('index')
        
class NonBlockingHandler(tornado.web.RequestHandler):
    executor = ThreadPoolExecutor(4)
    @gen.coroutine
    def get(self):
        try:
            start = time.time()
            # 并行执行
            result1, result2 = yield gen.with_timeout(datetime.timedelta(seconds=5), [self.doing(1), self.doing(2)], quiet_exceptions=tornado.gen.TimeoutError)
            self.write("NO Timeout")
            print(result1, result2)
            print(time.time() - start)
        except gen.TimeoutError:
            self.write("Timeout")
            print("Timeout")
            print(time.time() - start)
            
    # 使用tornado 线程池需要加上下面的装饰器到I/O函数
    @run_on_executor
    def doing(self, num):
        time.sleep(10)
        return 'Non-Blocking%d' % num
        
application = tornado.web.Application([
    (r"/index", IndexHandler),
    (r"/nonblocking", NonBlockingHandler),
])
if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
```

### 多进程运行

```
#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Python 3.5
import tornado.web
from tornado import gen
from tornado.httpserver import HTTPServer
class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('index')
        
@gen.coroutine
def doing():
    yield gen.sleep(10)
    raise gen.Return('Non-Blocking')
    
class NonBlockingHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self):
        result = yield doing()
        self.write(result)
        
def make_app():
    return tornado.web.Application([
        (r"/index", IndexHandler),
        (r"/nonblocking", NonBlockingHandler),
    ])
def main():
    app = make_app()
    server = HTTPServer(app)
    server.bind(8888)
    server.start(2)  # 设置启动多少个进程
    tornado.ioloop.IOLoop.current().start()
if __name__ == "__main__":
    main()
```