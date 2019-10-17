
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

