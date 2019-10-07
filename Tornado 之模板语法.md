## Tornado 之模板语法



#### [官方网址](https://tornado-zh.readthedocs.io/zh/latest/template.html)



#### 路径与渲染

​		使用模板、需要仿照静态文件设置一样，向web.Application类的构造函数中传递一个名为template_path的参数告诉Tornado从文件系统的一个特定位置提供模块文件，如：

```python
if __name__ == "__main__":
    tornado.options.parse_command_line()

    app = tornado.web.Application(
        [
            (r"/", IndexHandler)  # 注意路径结尾没有/
        ],
        static_path = os.path.join(os.path.dirname(__file__),"static")
    )

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
```

上面的配置会使得网页可以访问到我们的静态文件



#### StaticFileHandlder

​		我们在看看刚刚访问的页面使用的路径很长（http://127.0.0.1:8000/static/html/index.html），这对用户是相当不友好的，所以我们可以通过tornado.web.StaticFileHandler来自由映射静态文件路径url；之后我们可以访问：（http://127.0.0.1:8000/index.html）

```python
import json,os
import  tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.options
from tornado.options import options,define
from tornado.web import RequestHandler,StaticFileHandler

define("port",default=8000,type=int)

if __name__ == "__main__":
    tornado.options.parse_command_line()
    current_path = os.path.dirname(__file__)
    app = tornado.web.Application(
        [
            ....
            # 使用自带的类来处理静态文件访问，但是它会截胡所有路径，所以放最后
            (r"/(.*)",StaticFileHandler,{"path":os.path.join(current_path,"static/html")})
        ],
        #添加静态文件
        static_path = os.path.join(current_path,"static")
    )

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()

```



#### 模板

- 简单的使用模板，返回一个页面

  ```python
  import json,os
  import  tornado.web
  import tornado.ioloop
  import tornado.httpserver
  import tornado.options
  from tornado.options import options,define
  from tornado.web import RequestHandler,StaticFileHandler
  
  define("port",default=8000,type=int)
  
  class IndexHandler(RequestHandler):
      def get(self):
          # 取定义的摸版路径下查找index.html文件
          self.render("index.html")
  
  if __name__ == "__main__":
      tornado.options.parse_command_line()
      current_path = os.path.dirname(__file__)
      app = tornado.web.Application(
          [
              (r"/", IndexHandler),  
              # 屏蔽静态文件真实路径，直接使用即可，一般放最后
              (r"/(.*)",StaticFileHandler,{"path":os.path.join(current_path,"static/html"),"default_filename":"index.html"})
          ],
          #静态文件路径
          static_path = os.path.join(current_path,"static"),
          #静态模板文件路径
          template_path=os.path.join(current_path, "template")
      )
  
      http_server = tornado.httpserver.HTTPServer(app)
      http_server.listen(options.port)
      tornado.ioloop.IOLoop.current().start()
  ```

  

#### 模板语法

- 变量表达式

  在tornado的模板中使用{{}} 作为变量或者表达式的占位符，使用render渲染占位符{{}} 会被替换为相应的结果值；但是区别于Django的是，这里的变量表达式支持运算

  ```python
  <body>
      <a href=""><img src="/static/img/1.jpg" alt=""></a>
      价格:{{price}}
      数量:{{num}}
      总价:{{price * num}}
  </body>
  
   #{% if *condition* %}...{% elif *condition* %}...{% else %}...{% end %}
  ```

  后端代码

  ```python
  import json,os
  import  tornado.web
  import tornado.ioloop
  import tornado.httpserver
  import tornado.options
  from tornado.options import options,define
  from tornado.web import RequestHandler,StaticFileHandler
  
  define("port",default=8000,type=int)
  
  class IndexHandler(RequestHandler):
      def get(self):
          data = {
              "price":200,
              "num":3
          }
          #self.render("index.html",price=100,num=4)
          self.render("index.html",**data)
  
  if __name__ == "__main__":
      tornado.options.parse_command_line()
      current_path = os.path.dirname(__file__)
      app = tornado.web.Application(
          [
              (r"/", IndexHandler),
              # 屏蔽静态文件真实路径，直接使用即可，一般放最后
              (r"/(.*)",StaticFileHandler,{"path":os.path.join(current_path,"static/html"),"default_filename":"index.html"})
          ],
          #静态文件路径
          static_path = os.path.join(current_path,"static"),
          #静态模板文件路径
          template_path=os.path.join(current_path, "template")
      )
  
      http_server = tornado.httpserver.HTTPServer(app)
      http_server.listen(options.port)
      tornado.ioloop.IOLoop.current().start()
  ```

- 控制/循环语句：可以在Tornado模板中使用Python条件和循环语句。控制语句以{% %} 包围，并以类似下面的形式被使用

  ```python
  <body>
  <!-- if 判断-->
      {% if price*num == 400 %}
          价格:400
      {% elif price *num ==300 %}
          价格：300
      {% else %}
          价格未知
      {%  end %}
  
  <!-- for循环-->
      {% for index,value in enumerate(range(num)) %}
          个数：{{value}}
      {% end %}
  </body>
  
   #这和 python 的for 是一样的。 {% break %} 和 {% continue %} 语句是可以用于循环体之中的。
  ```

- 模板替换/继承

  ```
  	<!-- base.html -->
      <title>{% block title %}Default title{% end %}</title>
  
      <!-- mypage.html -->
      {% extends "base.html" %}
      {% block title %}My page title{% end %}
   
   
   {% include *filename* %} 引入模板文件
   {% extends *filename* %} 模板继承
  ```

- 转义相关

  ```
  {% raw text %}   将传入的变量text不进行转义输出，显示原始格式
  
  {% autoescape None %} 自动转义 ，关闭转移后可以使用 {{escape(text)}} 来进行转义
  ```

- 自定义函数

  ```python
  <body>
      总价：{{ func_total(price,num) }}
  </body>
  
  后端代码：
  import json,os
  import  tornado.web
  import tornado.ioloop
  import tornado.httpserver
  import tornado.options
  from tornado.options import options,define
  from tornado.web import RequestHandler,StaticFileHandler
  
  define("port",default=8000,type=int)
  
  def total_price(price,num):
      return price * num
  
  class IndexHandler(RequestHandler):
      def get(self):
          #传入函数名
          self.render("index.html",price=100,num=4,func_total=total_price)
  
  if __name__ == "__main__":
      tornado.options.parse_command_line()
      current_path = os.path.dirname(__file__)
      app = tornado.web.Application(
          [
              (r"/", IndexHandler),
              # 屏蔽静态文件真实路径，直接使用即可，一般放最后
              (r"/(.*)",StaticFileHandler,{"path":os.path.join(current_path,"static/html"),"default_filename":"index.html"})
          ],
          #静态文件路径
          static_path = os.path.join(current_path,"static"),
          #静态模板文件路径
          template_path=os.path.join(current_path, "template")
      )
  
      http_server = tornado.httpserver.HTTPServer(app)
      http_server.listen(options.port)
      tornado.ioloop.IOLoop.current().start()
  ```

  





