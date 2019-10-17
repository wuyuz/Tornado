## Tornado 之请求与响应



#### 请求中的方法

- 获取查询字符串参数
  - get_query_argument(name,default=_ARG_DEFAULT,strip=True)

  ​       从请求的查询字符串中返回指定参数name的值，如果出现多个同名参数，则返回最后一个的值

  ```
  参数：
  	defaulte：为设置name参数时，使用的默认值，若defalut未设置则抛错 MissiongArgmentError
  	strip：表示是否过滤掉左右两边的空白字符，默认过滤
  	_ARG_DEFAULT:用于抛错
  ```

  - get_query_arguments(name,strip=True)

    从请求的查询字符串中返回指定参数name的值，注意返回的是list列表（即使对应name参数只有一个值）若未找到name参数，则返回空列表

    

- 获取请求体参数

  - get_body_argument(name,default=_ARG_DEFAULT,strip=True)

    从请求体中返回指定参数name的值，如果出现多个同名参数，则返回最后一个的值

  - get_body_arguments(name,strip=True)

    从请求体中的查询字符串中返回指定参数name的值，注意返回的是list列表

  ```python
  import tornado.web  # tornado的基础web框架
  import tornado.ioloop  # tornado 的核心IO循环模块，封装了Linux的epoll模块，高性能基础
  import tornado.httpserver
  import tornado.options
  
  from tornado.options import define, options  # 导入定义操作函数
  from tornado.web import RequestHandler, url  # 导入请求接口，和路由函数
  
  # options 是可以全局定义一些变量，以便于全局调用options.port,这里定义了一个port
  tornado.options.define("port", type=int, default=9990, help="服务器端口")
  
  
  # 主页处理逻辑，相当于视图
  class IndexHandler(RequestHandler):
  
      def get(self):
          #请求中的参数
          subject = self.get_argument("subject")
          subjects = self.get_arguments("subject")
  
          subject1 = self.get_query_arguments("subject")
          self.write("subject=%s,subjects=%s,subject1=%s,"%(subject,subjects,subject1))
  	
      #请求体中的数据一般在post方法中
      def post(self):
          subject = self.get_argument("subject")
          subjects = self.get_arguments("subject")
          subject1 = self.get_query_arguments("subject")
          self.write("subject=%s,subjects=%s,subject1=%s," % (subject, subjects, subject1))
  
          subject2 = self.get_body_argument("name")
          self.write("subject=%s"%subject2)
  
  if __name__ == "__main__":
      tornado.options.parse_command_line()
  
      app = tornado.web.Application(
          [
              (r"/", IndexHandler),
          ],
          debug=True
      )
      http_server = tornado.httpserver.HTTPServer(app)
      # 给服务器实例绑定端口
      http_server.listen(options.port)
      tornado.ioloop.IOLoop.current().start()
  ```

- 获取所有参数中的值，是对前两类方法的整合

  get_argument(name,default=_ARG_DEFAULT,strip=True)  返回单个参数对应的值

  get_arguments(name,default=_ARG_DEFAULT,strip=True) 返回参数对应的值列表

- 关于请求的其他信息

  ```
  RequestHandler.request 对象存储了关于请求的相关信息，具体属性有：
  
  method HTTP的请求方式，如GET或POST
  host 被请求的主机名
  uri 请求的完整资源标识，包含路径和查询字符串
  path 请求路径部分
  query 请求的查询字符串部分，参数部分
  version 使用的HTTP请求版本
  headers 请求的协议头，是类字典型对象，支持关键字索引凡是获取特定协议头信息，例如：
  	request.headers["Content-type"]
  body 请求体数据
  remote_ip 客户端ip地址
  files 用户上传文件，为字典类型，如：
  	{
  		"form_filename1":[<tornado.httputil.HTTPFile>,...],
  		...
  	}
  	tornado.httputil.HTTPFile是接收到的文件对象，它有三个属性：
  		filename : 文件的实际名字，form_filename1，对应的是是表单对应的名字，不是文件名字
  		body: 文件实体部分
  		content_type: 文件类型
  ```

  - 获取json数据，在其他框架中获取json数据都是很简单的

    ```python
    import json
    import  tornado.web
    import tornado.ioloop
    import tornado.httpserver
    import tornado.options
    from tornado.options import options,define
    from tornado.web import RequestHandler
    
    define("port",default=8000,type=int)
    
    class IndexHandler(RequestHandler):
        def get(self):
            print(self.request.path)
            print(self.request.headers)
            self.write("Hello world")
    
        def post(self):
            print(self.request.headers)
            # 获取json数据，首先判断请求体格式，如果满足要求就从body中取出，反序列化
            if self.request.headers.get("Content-Type") == "application/json":
                json_data = self.request.body
                json_args = json.loads(json_data)
                print(json_args,type(json_args))   #{'a': '666'} <class 'dict'>
            self.write("Post content : %s"%json_args)
    
    
    if __name__ == "__main__":
        tornado.options.parse_command_line()
    
        app = tornado.web.Application(
            [
                (r"/",IndexHandler),
            ]
        )
    
        http_server = tornado.httpserver.HTTPServer(app)
        http_server.listen(options.port)
        tornado.ioloop.IOLoop.current().start()
    
    ```

  - 上传图片功能

    ```python
    import json
    import  tornado.web
    import tornado.ioloop
    import tornado.httpserver
    import tornado.options
    from tornado.options import options,define
    from tornado.web import RequestHandler
    
    define("port",default=8000,type=int)
    
    class UploadHandler(RequestHandler):
        def post(self):
            files = self.request.files
            img_files = files.get('img')
            if img_files:
                img_file = img_files[0]['body']
                file = open("./wang.jpg",'wb+')
                file.write(img_file)
                file.close()
            self.write("OK")
    
    if __name__ == "__main__":
        tornado.options.parse_command_line()
    
        app = tornado.web.Application(
            [
                (r"/uploader",UploadHandler),
            ]
        )
    
        http_server = tornado.httpserver.HTTPServer(app)
        http_server.listen(options.port)
        tornado.ioloop.IOLoop.current().start()
        
     可使用postman中的form-data格式传输文件
    ```

以上的方法，是对于请求体中的数据要求为字符串，且格式为表单编码格式（与url中的请求字符字符串格式相同），即key1=value&key2=value2; HTTP请求头中的 Content-Type为“application/x-www-form-urlencode或者

form-data。 但是对于请求数据是json/xml的是无法获取到数据的



#### 正则提取URL，传参

 		tornado中对于路由映射也支持正则提取url，提取出来的参数会作为RequestHandler中对应请求方式的成员方法参数。若在正则表达式中定义了名字， 则参数按名传递；如参数按顺序传递，提取出阿里的额参数会作为对应的请求方式的成员方法的参数

```python
import  tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.options
from tornado.options import options,define
from tornado.web import RequestHandler

define("port",default=8000,type=int)

class SubjectCityHandler(RequestHandler):
    def get(self,subject,city):
        self.write("Subject: %s<br/>City:%s"%(subject,city))


class SubjectDateHandler(RequestHandler):
    def get(self, date, subject):
        self.write("Date: %s<br/>Subject:%s" % (date, subject))

if __name__ == "__main__":
    tornado.options.parse_command_line()

    app = tornado.web.Application(
        [
            # 无名传参
            (r"/sub-city/(.+)/([a-z]+)",SubjectCityHandler),
            # 命名传参
            (r"/sub-date/(?P<subject>.+)/(?P<date>[a-z]+)", SubjectDateHandler),
        ]
    )

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()

访问：http://127.0.0.1:8000/sub-city/sd/cq
```



#### 响应

- write(chunk)  将chunk数据写到输出缓冲区中，如我们之前写的返回的数据

  ```python
  class SubjectCityHandler(RequestHandler):
      def get(self,subject,city):
          self.write("Subject: %s<br/>City:%s"%(subject,city))
  ```

  想一想，可不可以同一处理方法多次使用write方法？

  ```python
  class IndexHandler(RequestHandler):
      def get(self):
          self.write("首页")
          self.write("首页1")
          self.write("首页2")
          
    #是可以的，write方法是写到缓冲区中，我们可以象写文件一样多次追加，最后一次输出，当我们结束get方法时执行self.finish()函数
  ```

  想一想如果写入json数据类型

  ```python
  import json
  class IndexHandler(RequestHandler):
      def get(self):
          stu = {
              "name":"zs",
              "age":24,
              "gender":1,
          }
          stu_json = json.dumps(stu)
          self.write(stu_json)
   
   # 实际上，我们可以不用自己手动做json序列化，当write方法检测到我们传入的chunk参数是字段后，会自动帮我们转换为json字符串
  class IndexHandler(RequestHandler):
      def get(self):
          stu = {
              "name":"zs",
              "age":24,
              "gender":1,
          }
          self.write(stu)
          
   #两种方式的区别：对比一下两种方式的响应头header中的Content-Type字段， 自己手动设置的为：text/html;charset=UTF-8,而采用write方法时为 Content-Type：application/json，所以我们最号还是使write(字典)，也就是说write会根据我们传入的字典，把改为 Content-Type：application/json
  ```

  

- set_header(name,value)

  利用set_header(name,value)方法，可以手动设置一个名为name、值为value的响应头的header字段，直接使用write(字典)，会自动完成设置，如果我们使用json，那么就要手动设置了

  ```python
  class IndexHandler(RequestHandler):
      def get(self):
          stu = {
              "name":"zs",
              "age":24,
              "gender":1,
          }
          stu_json = json.dumps(stu)
          self.write(stu)
          self.set_header("Content-Type","application/json;charset=UTF-8")
  ```

- set_default_headers()

  该方法会在进入HTTP处理方法前先调用，可以重写此方法来预先设置默认的headers。注意：在HTTP处理方法中使用set_header()方法会覆盖掉此方法设置的同名header

  ```python
  class IndexHandler(RequestHandler):
  
      def set_default_headers(self) :
          print("执行了set_default_headers()方法")
          self.set_header("name","python")
  
      def get(self):
          stu = {
              "name":"zs",
              "age":24,
              "gender":1,
          }
          stu_json = json.dumps(stu)
          self.write(stu)
          self.set_header("Content-Type","application/json;charset=UTF-8")
  ```

- set_status(status_code,reason=None)

  为响应设置状态码

  

- redirect(url) 重定向

  告诉浏览器跳转url

  ```python
  import  tornado.web
  import tornado.ioloop
  import tornado.httpserver
  import tornado.options
  from tornado.options import options,define
  from tornado.web import RequestHandler,url
  
  define("port",default=8000,type=int)
  
  class IndexHandler(RequestHandler):
      def get(self):
         self.write("主页")
  
  class LoginHandler(RequestHandler):
      def get(self):
          self.write('<form method="post"><input type="submit" value="登陆"></form>')
  
      def post(self):
          # self.redirect("/")
          self.redirect(self.reverse_url("login"))
  
  if __name__ == "__main__":
      tornado.options.parse_command_line()
  
      app = tornado.web.Application(
          [
              # 方式一：
              # (r"/", IndexHandler)
              # (r"/xxx",LoginHandler)
  
              #方式二：
              url(r"/",IndexHandler,name='login'),
              url(r"/xxx",LoginHandler,)
          ]
      )
  
      http_server = tornado.httpserver.HTTPServer(app)
      http_server.listen(options.port)
      tornado.ioloop.IOLoop.current().start()
  ```

  

- send_err(status_code=500,**kwargs)

  抛出HTTP错误状态码，默认500，kwargs为可变命名参数，使用send_error抛出错误后tornado会调用write_error()方法处理，并返回给浏览器

  ```python
  class IndexHandler(RequestHandler):
  
      def get(self):
          self.write("主页")
          self.send_error(404,content="出现404")
          
    #默认：write/send_error方法不会处理send/write_error抛出的参数的，及上面的content参数是没有意义的，所以要配合着write_error使用
  ```

- write_error(status_code,**kwargs)

  用来处理send_error抛出的错误信息并返回给浏览器错误信息页面，可以重写此方法来定制自己的错误显示页面

  ```python
  class IndexHandler(RequestHandler):
  
      def get(self):
          self.send_error(404,title='abc',content='出错了')
  
      def write_error(self, status_code: int, **kwargs: str) -> None:
          self.write("出错了<br/>")
          self.write("标题：%s<br/>"%kwargs.get("title",'none'))
          self.write("详情：%s<br/>"%kwargs.get("content",'none'))
  ```

- set_cookie(key, val, expires,expires_day)  ： 设置cookie,可使用 timedelta 来加减时间
- clear_cookie('token') 删除该键的值





#### 请求参数方法补充

- initialize()

  对应每个请求的处理类Handler在构造一个实例后首先执行initialize()方法。在讲输入时提到，路由映射中的第三个字典型参数会作为该方法的命名参数传递，如：

  ```python
  import  tornado.web
  import tornado.ioloop
  import tornado.httpserver
  import tornado.options
  from tornado.options import options,define
  from tornado.web import RequestHandler,url
  
  database = {
      'name':'wang'
  }
  
  define("port",default=8000,type=int)
  
  class IndexHandler(RequestHandler):
  
      def initialize(self,database):
          self.database = database
  
      def get(self,xxx):
          self.write(xxx)  # 这里时url路径上传递的参数
          self.write(self.database)  # 这是后期传入的补充参数
  
  if __name__ == "__main__":
      tornado.options.parse_command_line()
  
      app = tornado.web.Application(
          [
              (r"/user/(.*)", IndexHandler,dict(database=database))
          ]
      )
  
      http_server = tornado.httpserver.HTTPServer(app)
      http_server.listen(options.port)
      tornado.ioloop.IOLoop.current().start()
      
   #http://127.0.0.1:8000/user/ok
  ```

- prepare() 

  预处理，即在执行对应请求方式的HTTP方法前执行i，注意： 不论以何种HTTP方式请求，都会执行prepare()方法，判断响应数据

  ```python
  import json
  import  tornado.web
  import tornado.ioloop
  import tornado.httpserver
  import tornado.options
  from tornado.options import options,define
  from tornado.web import RequestHandler,url
  
  define("port",default=8000,type=int)
  
  class IndexHandler(RequestHandler):
      def prepare(self):
          print(self.request.headers)
          if self.request.headers.get("Content-Type","").startswith('application/json'):
              self.json_dict = json.loads(self.request.body)
          else:
              self.json_dict = None
  
      def post(self):
          if self.json_dict:
              for key, value in self.json_dict.items():
                  self.write("<h3>%s</h3><p>%s</p>"%(key,value))
  
  
  if __name__ == "__main__":
      tornado.options.parse_command_line()
  
      app = tornado.web.Application(
          [
              (r"/user", IndexHandler)  # 注意路径结尾没有/
          ]
      )
  
      http_server = tornado.httpserver.HTTPServer(app)
      http_server.listen(options.port)
      tornado.ioloop.IOLoop.current().start()
  ```

- on_finish()

  在请求处理结束后调用，即在调用HTTP方法之后调用

- 各个方法调用顺序

  ![1570433064127](C:\Users\wanglixing\Desktop\知识点复习\Tornado\1570433064127.png)



#### [其他的响应参数讲解](https://tornado-zh.readthedocs.io/zh/latest/web.html#id1)