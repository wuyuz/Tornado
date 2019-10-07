## Tornado 基本模块



#### tornado.httpserver 模块

​		用于创建一个绑定应用的服务器，针对于该应用的路由来启动特定的服务器，在上一章中我们使用app.listen()去监听所有的请求，这里我们将使用自己的server来监听

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
	    
    #app.listen(8000)  #app自己创建服务器并监听listen
    #创建服务器
    http_server = tornado.httpserver.HTTPServer(app)
    #给服务器实例绑定端口
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()
```

- 单进程与多进程

  ​		默认情况下，tornado服务启动的是单进程，那么如何启动多进程？

  ```python
  if __name__ == "__main__":
      tornado.options.parse_command_line()
  
      # 实例化一个app，Application：是tornado web框架核心，是与服务器的接口
      app = tornado.web.Application(
          [
              (r"/",IndexHandler)
          ],
          debug=True
      )
  
      http_server = tornado.httpserver.HTTPServer(app)
      # http_server.listen(options.port)
  
      http_server.bind(8000) # 给服务器绑定端口
      http_server.start(5)  # 默认是1，这里启动的5个进程，当小于0时，开启对应硬件cpu核数个子进程
      tornado.ioloop.IOLoop.current().start()
  ```

  虽然tornado提供了多进程启动的方式，但是并不建议使用：

  - 每个子进程都会从父进程中复制IOLoop实例，如果创建子进程前修改IOLoop，会影响所有的子进程
  - 所有进程共享一个端口，分别控制困难



#### tornado.options模块

​		tornado为我们提供了一个tornado.options模块，可以进行全局参数的定义、存储、转换

- tornado.options.define()  用于定义options选项变量的方法

  ```
  参数：
  	name：选项变量名
  	default：设置选项默认值，默认None
  	type: 设置变量类型，可以是str,datetime,int
  	help：帮助文档
  	multiple:设置选项变量是否可以为多个值，默认为False，如要传入列表
  ```

- tornado.options.parse_command_line()  转换命令行中的参数，并保存到全局options中，相当于保存到options中

  ```python
  import tornado.web  # tornado的基础web框架
  import tornado.ioloop  # tornado 的核心IO循环模块，封装了Linux的epoll模块，高性能基础
  import tornado.httpserver
  import tornado.options
  
  from tornado.options import define,options  # 导入定义操作函数
  from tornado.web  import RequestHandler,url  # 导入请求接口，和路由函数
  
  # options 是可以全局定义一些变量，以便于全局调用options.port,这里定义了一个port
  tornado.options.define("port",type=int,default=8000,help="服务器端口")
  tornado.options.define("list",type=str,default=[],multiple=True)
  
  #主页处理逻辑，相当于视图
  class IndexHandler(RequestHandler):
  
      def get(self):
          self.write('Hello world！')
  
  if __name__ == "__main__":
      # 转换命令行参数到options中
      tornado.options.parse_command_line()
  
      # 因为这里是需要从命令行传入参数，所以需要使用命令行启动
      print("list= ",options.list)
  
      # 实例化一个app，Application：是tornado web框架核心，是与服务器的接口
      app = tornado.web.Application(
          [
              (r"/",IndexHandler),
          ],
          debug=True
      )
  
      http_server = tornado.httpserver.HTTPServer(app)
      http_server.listen(options.port)
  
      tornado.ioloop.IOLoop.current().start()
  
  启动：
  	> python ./torna/1.py --port=9000 --list=good,nice
  ```

- tornado.options.parse_config_file(path)  从配置文件导入参数

  - 代码示例

    ```python
    import tornado.web  # tornado的基础web框架
    import tornado.ioloop  # tornado 的核心IO循环模块，封装了Linux的epoll模块，高性能基础
    import tornado.httpserver
    import tornado.options
    
    from tornado.options import define,options  # 导入定义操作函数
    from tornado.web  import RequestHandler,url  # 导入请求接口，和路由函数
    
    # options 是可以全局定义一些变量，以便于全局调用options.port,这里定义了一个port
    tornado.options.define("port",type=int,default=8000,help="服务器端口")
    tornado.options.define("list",type=str,default=[],multiple=True)
    
    #主页处理逻辑，相当于视图
    class IndexHandler(RequestHandler):
    
        def get(self):
            self.write('Hello world！')
    
    if __name__ == "__main__":
        # 从文件中读取参数到options中
        tornado.options.parse_config_file("./config")
    
        # 因为这里是需要从命令行传入参数，所以需要使用命令行启动
        print("list= ",options.list)
    
        # 实例化一个app，Application：是tornado web框架核心，是与服务器的接口
        app = tornado.web.Application(
            [
                (r"/",IndexHandler),
            ],
            debug=True
        )
    
        http_server = tornado.httpserver.HTTPServer(app)
        http_server.listen(options.port)
    
        tornado.ioloop.IOLoop.current().start()
    ```

  - config文件

    ```
    port = 7000
    list = ["good","nice"]
    ```

- 常用导入参数的方式：因为上面的文件配置方式不支持字典类型

  - 示例

    ```python
    import tornado.web  # tornado的基础web框架
    import tornado.ioloop  # tornado 的核心IO循环模块，封装了Linux的epoll模块，高性能基础
    import tornado.httpserver
    from torna import congfig
    
    from tornado.options import define,options  # 导入定义操作函数
    from tornado.web  import RequestHandler,url  # 导入请求接口，和路由函数
    
    
    #主页处理逻辑，相当于视图
    class IndexHandler(RequestHandler):
    
        def get(self):
            self.write('Hello world！')
    
    if __name__ == "__main__":
    
        print("list= ",congfig.options["list"])
    
        # 实例化一个app，Application：是tornado web框架核心，是与服务器的接口
        app = tornado.web.Application(
            [
                (r"/",IndexHandler),
            ],
            debug=True
        )
    
        http_server = tornado.httpserver.HTTPServer(app)
        http_server.listen(congfig.options["port"])
        tornado.ioloop.IOLoop.current().start()
    ```

  - 创建一个名为config.py的普通文件

    ```
    #参数
    options = {
        "port":8000,
        "list":["good","nice","OK"]
    }
    ```

    

#### 日志功能

​		当我们在代码中使用parse_command_line()或者parse_config_file(path)方法时，tornada会默认开启logging模块功能，向屏幕终端输出访问日志信息

- 关闭日志

  ```
  1、如果使用配置文件的方式时：
  	if __name__ == "__main__":
          # 从文件中读取参数到options中
          tornado.options.parse_config_file("./config")
          #关闭日志功能
          tornado.options.options.logging = None  
  
  2、启动命令中 >python ./torna/1.py --logging=none
  ```

  