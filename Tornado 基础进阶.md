## Tornado 基础进阶



#### 将APP进行函数封装

- 代码如下

  ```python
  import tornado.ioloop
  import tornado.web
  
  class MainHandler(tornado.web.RequestHandler):
  
      def get(self):
          self.write("Hello world")
  
  
  def make_app():
      return tornado.web.Application(handlers=[
          (r'/',MainHandler),
      ])
  
  if __name__ == '__main__':
      # 启动
      app = make_app()
      # 监听端口
      app.listen(80)
      tornado.ioloop.IOLoop.current().start()
  ```

- 为了在启动的使用端口可配置，我们常常需要配置options

  ```python
  import tornado.ioloop
  import tornado.web
  from tornado.options import define,options,parse_command_line
  
  # 全局定义变量,默认为80，如果不写的话为80
  define('port',default=80, type=int)
  
  class MainHandler(tornado.web.RequestHandler):
  
      def get(self):
          self.write("Hello world")
  
  
  def make_app():
      return tornado.web.Application(handlers=[
          (r'/',MainHandler),
      ])
  
  if __name__ == '__main__':
      # 解析启动命令,将port参数对应的值提取，也就是说我们可以通过在命令行输入：
      # python 1.py --port=80 启动
      parse_command_line()
      # 启动
      app = make_app()
      # 监听端口
      app.listen(options.port)
      tornado.ioloop.IOLoop.current().start()
  ```

- 使用切入点函数，对请求的到来和结束进行处理，相当于中间件

  ```python
  import tornado.ioloop
  import tornado.web
  from tornado.options import define,options,parse_command_line
  import pymysql
  
  # 全局定义变量,默认为80，如果不写的话为80
  define('port',default=80, type=int)
  
  class MainHandler(tornado.web.RequestHandler):
      def initialize(self):
          # 实现功能是，创建连接对象
          self.conn = pymysql.Connection(host='127.0.0.1',password='123',database='spider',user='root',port=3306)
          self.cursor = self.conn.cursor()
          print('初始化数据连接')
          
      def prepare(self):
          print('预处理方法')
  
      def get(self):
          # 实现功能是，访问数据库，查询学生的所有信息
          sql = 'select * from admin'
          self.cursor.execute(sql)
          data = self.cursor.fetchall()
          print(data)
          self.write('查询数据')
  
      def on_finish(self) -> None:
          # 在最后关闭连接，以防止多次创建连接
          self.cursor.close()
          print('关闭连接对象')
  
  def make_app():
      return tornado.web.Application(handlers=[
          (r'/',MainHandler),
      ])
  
  if __name__ == '__main__':
      # 解析启动命令,将port参数对应的值提取，也就是说我们可以通过在命令行输入：
      # python 1.py --port=80 启动
      parse_command_line()
      # 启动
      app = make_app()
      # 监听端口
      app.listen(options.port)
      tornado.ioloop.IOLoop.current().start()
  ```

  

#### 模板语法

- 模板继承

  base.html

  ```
  <!DOCTYPE html>
  <html lang="en">
  <head>
      <meta charset="UTF-8">
      <title>
          {% block title %} {% end %}
      </title>
  </head>
  <body>
      {% block content %} {% end %}
  </body>
  </html>
  ```

  index.html

  ```
  {% extends 'base.html' %}
  
  {% block title %}
      首页
  {% end %}
  
  {% block content %}
      <p>Hello</p>
  {% end %}
  ```

  py文件

  ```python
  import tornado.ioloop
  import tornado.web
  from tornado.options import define,options,parse_command_line
  import os
  
  # 全局定义变量,默认为80，如果不写的话为80
  define('port',default=80, type=int)
  
  class IndexHandler(tornado.web.RequestHandler):
      def get(self):
          # 内置模板语法函数
          self.render("index.html")
  
  def make_app():
      return tornado.web.Application(
          handlers=[
              (r'/index',IndexHandler),
          ],
          # 要设置模板文件位置，不设置同级可以使用
          template_path=os.path.join(os.path.dirname(__file__),'template'),
      )
  
  if __name__ == '__main__':
      # 解析启动命令,将port参数对应的值提取，也就是说我们可以通过在命令行输入：
      # python 1.py --port=80 启动
      parse_command_line()
      # 启动
      app = make_app()
      # 监听端口
      app.listen(options.port)
      tornado.ioloop.IOLoop.current().start()
  ```

- tornado项目格式：类似于Flask项目

  ![1570626216807](C:\Users\wanglixing\Desktop\知识点复习\Django\gif\1570626216807.png)

  manage.py

  ```python
  import os
  import tornado.web
  import tornado.ioloop
  from  tornado.options import options,define,parse_command_line
  define('port',default=80,type=int)
  
  from app.views import IndexHandler
  
  def make_app():
      return tornado.web.Application(
          handlers=[
              (r'/index',IndexHandler),
          ],
          template_path=os.path.join(os.path.dirname(__file__),'templates'),
      )
  
  if __name__ == '__main__':
      parse_command_line()
      app = make_app()
      app.listen(options.port)
      tornado.ioloop.IOLoop.current().start()
  ```

  app/views.py

  ```python
  import tornado
  
  class IndexHandler(tornado.web.RequestHandler):
  
      def get(self):
          self.render("index.html")
  ```

- 模板语法补充

  ```html
  1、异常处理
  <body>
      {% try %}
          {{ int('牛') }}
      {% except %}
          <p>无法转换</p>
      {% finally %}
          <p>必须执行的操作</p>
      {% end %}
  </body>
  
  2、set变量
  <body>
      {% set n= 100 %}
      <p>{{n}}</p>
  </body>
  
  3、while的用法
  <body>
      {% while len(items) %}
      <p>{{ item.pop() }}</p>
      {% end %}
  </body>
  ```



#### 静态文件路径

- 代码如下

  ```python
  def make_app():
      return tornado.web.Application(
          handlers=[
              (r'/index',IndexHandler),
          ],
          # 模板文件
          template_path=os.path.join(os.path.dirname(__file__),'templates'),
          # 静态文件路径
          static_path=os.path.join(os.path.dirname(__file__),'static'),
      )
  ```



#### ORM操作

![1570630086603](C:\Users\wanglixing\Desktop\知识点复习\Django\gif\1570630086603.png)

- 安装sqlalchemy

  ```
  pip3 install sqlalchemy
  ```

- manage.py

  ```python
  import os
  import tornado.web
  import tornado.ioloop
  from  tornado.options import options,define,parse_command_line
  define('port',default=80,type=int)
  
  from app.views import DbHandler,DropDbHandler,AddStuHandler,IndexHandler,StusHandler
  
  def make_app():
      return tornado.web.Application(
          handlers=[
              (r'/index',IndexHandler),
              (r'/init_db',DbHandler),
              (r'/drop_db', DropDbHandler),
              (r'/add_stu', AddStuHandler),
              (r'/stus',StusHandler),
          ],
          # 模板文件
          template_path=os.path.join(os.path.dirname(__file__),'templates'),
          # 静态文件路径
          static_path=os.path.join(os.path.dirname(__file__),'static'),
      )
  
  if __name__ == '__main__':
      parse_command_line()
      app = make_app()
      app.listen(options.port)
      tornado.ioloop.IOLoop.current().start()
  ```

- app/views.py

  ```python
  import tornado
  from app.models import create_db, drop_db, Student
  from utils.conn import session
  
  class IndexHandler(tornado.web.RequestHandler):
  
      def get(self):
          self.render("index.html")
  
  # 创建表
  class DbHandler(tornado.web.RequestHandler):
  
      def get(self):
          create_db()
          self.write('创建成功，数据库迁移')
  
  #删除表
  class DropDbHandler(tornado.web.RequestHandler):
  
      def get(self):
          drop_db()
          self.write('删除数据库')
  
  #新增数据
  class AddStuHandler(tornado.web.RequestHandler):
      def post(self):
          # 创建单条数据
          stu = Student()  # 导入表类，并实例化对象
          stu.s_name = '小明'
          session.add(stu)
          session.commit()  #提交数据到数据库
          self.write('新增数据成功')
  
  # 对学生的查，删
  class StusHandler(tornado.web.RequestHandler):
  
      def get(self):
          stu= session.query(Student).filter(Student.s_name=='小明').all()
          stu= session.query(Student).filter_by(s_name='小明').all()
          print(stu)
          self.write('查询数据成功')
  
      def delete(self):
          # 实现删除
          stu= session.query(Student).filter_by(s_name='小明').all()
          if stu:
              session.delete(stu)
              session.commit()
              self.write('删除成功')
          else:
              self.write('删除失败')
  
          # 第二种：调用delete()方法
          #session.query(Student).filter(Student.s_name=='小明').delete()
  
  
      def patch(self):
          stu = session.query(Student).filter_by(s_name='小明').first()
          stu.s_name='小花'
          session.add(stu)
          session.commit()
  
          # 方式二：update，如果是列表，所有的名字都为小花
          stu = session.query(Student).filter_by(s_name='小明').update({'s_name':'小花'})
          session.commit()
          self.write('修改成功')
  ```

- app/models.py

  ```python
  from sqlalchemy import Column, Integer,INTEGER,String
  from utils.conn import Base
  
  # 创建表
  def create_db():
      Base.metadata.create_all()
  
  # 删除表
  def drop_db():
      Base.metadata.drop_all()
  
  
  # 我们写的model类必须继承与来自数据库连接引擎的基类Base
  class Student(Base):
      # 主键自增的int类型的id主键
      id = Column(Integer,primary_key=True,autoincrement=True)
      # 定义不能为空的唯一姓名字段
      s_name = Column(String(10),unique=True,nullable=False)
      a_age = Column(Integer,default=18)
  
      __tablename__ = 'student'
  
      def __repr__(self):
          # 格式化输出名字
          return self.s_name
  ```

- utils/conn.py

  ```python
  #连接数据库格式
  from sqlalchemy import create_engine
  from sqlalchemy.ext.declarative import declarative_base
  from sqlalchemy.orm import sessionmaker
  
  # 连接数据格式 mysql+pymysql://root:123@127.0.0.1:3306/tornado
  db_url = 'mysql+pymysql://root:123@127.0.0.1:3306/tornado'
  
  # 创建引擎，建立连接
  engine = create_engine(db_url)
  
  # 模型与数据库表进行关联的基类，模型必须继承与Base
  Base = declarative_base(bind=engine)
  
  # 创建session会话
  DbSession = sessionmaker(bind=engine)
  session = DbSession()
  ```

  