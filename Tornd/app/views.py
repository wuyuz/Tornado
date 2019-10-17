import tornado.websocket
import tornado.web


class IndexHandler(tornado.web.RequestHandler):

    def get(self):
        self.render("index.html")

class LoginHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.error = ''

    def get(self):
        self.render('login.html',error=self.error)

    def post(self):
        # 获取登录用户信息
        username = self.get_argument('username')
        password = self.get_argument('password')

        # 模拟登陆
        if username in ['coco','wang'] and password == '123':
            self.set_cookie('user',username)  #登陆成功存入cookie
            self.render('chat/chat.html',username=username)

        else:
            self.error = '用户密码错误'
            self.render('login.html',error=self.error)


class ChatHandler(tornado.websocket.WebSocketHandler):

    # 用于存放所有连接对象
    user_online = []

    # 长连接开始时 触发
    def open(self,*args,**kwargs):
        self.user_online.append(self)

        for user in self.user_online:
            # 当进入chat.html页面时，会主动出发该函数
            username = self.get_cookie('user')
            user.write_message('系统提示[%s已进入聊天室]'%username)

    # 对接前端websocket的send方法，接收并转发
    def on_message(self, message):
        user = self.get_cookie('user')
        for user_per in self.user_online:
            user_per.write_message('%s: %s'%(user,message))


    def on_close(self):
        # 移除连接对象, 失去websocket对象时自动触发
        self.user_online.remove(self)
        for user in self.user_online:
            username = self.get_cookie('user')
            user.write_message('系统提示:[%s退出聊天室]'%username)




