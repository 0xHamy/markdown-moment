from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database.database import Base 

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    yaml_id = Column(String(50), unique=True, nullable=False)
    title = Column(String(200), nullable=False)
    points = Column(Integer, default=0)
    creator_info = Column(Text)
    modules = relationship("Module", backref="course", lazy=True)

class Module(Base):
    __tablename__ = "modules"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    yaml_id = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    points = Column(Integer, default=0)
    order = Column(Integer, default=0)
    sections = relationship("Section", backref="module", lazy=True)
    exercise = relationship("Exercise", backref="module", uselist=False)

class Section(Base):
    __tablename__ = "sections"
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id"), nullable=False)
    yaml_id = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    points = Column(Integer, default=0)
    order = Column(Integer, default=0)

class Exercise(Base):
    __tablename__ = "exercises"
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id"), nullable=False)
    content = Column(Text, nullable=False)
    points = Column(Integer, default=0)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    points = Column(Integer, default=0)
    is_admin = Column(Boolean, default=False)

class Completion(Base):
    __tablename__ = "completions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    item_type = Column(String(20), nullable=False)
    item_id = Column(Integer, nullable=False)
