import os
import tornado.web
import tornado.ioloop
from  tornado.options import options,define,parse_command_line
define('port',default=80,type=int)

from app.views import IndexHandler,LoginHandler,ChatHandler

def make_app():
    return tornado.web.Application(
        handlers=[
            (r'/index',IndexHandler),
            (r'/login', LoginHandler),
            (r'/chat', ChatHandler),
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