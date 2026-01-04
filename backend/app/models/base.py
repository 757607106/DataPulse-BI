"""
基础模型定义
"""
from sqlalchemy.ext.declarative import declarative_base

# 创建基础类
Base = declarative_base()

# 这里可以定义通用的模型方法
class BaseModel(Base):
    """基础模型类"""
    __abstract__ = True

    def to_dict(self):
        """转换为字典"""
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
