from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, Boolean, Integer, String
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Session = scoped_session(sessionmaker(autocommit=False, autoflush=False))
Base = declarative_base()
Base.query = Session.query_property()

class Users(Base):
__tablename__ = 'users'
first_name = Column(String)
last_name = Column(String)
ssh_public_key = Column(String)
username = Column(String, primary_key=True)
site_id = Column(String, primary_key=True)
realm = Column(String, primary_key=True)
uid = Column(Integer)
id = Column(Integer, primary_key=True)
type = Column(String)
hdir = Column(String)
shell = Column(String)
email = Column(String)
active = Column(Boolean, server_default='true')

class UsersLogic(Users):
pass
engine = create_engine('postgresql://rsetti@localhost/mothership',pool_recycle=1800,echo=True)

Session.configure(bind=engine)
Base.metadata.create_all(engine)

us = UsersLogic()
