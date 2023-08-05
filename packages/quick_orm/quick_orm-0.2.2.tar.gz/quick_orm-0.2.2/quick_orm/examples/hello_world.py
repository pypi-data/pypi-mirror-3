from quick_orm.core import Database
from sqlalchemy import Column, String

class User(object):
    __metaclass__ = Database.DefaultMeta
    name = Column(String(30))

if __name__ == '__main__':
    database = Database('sqlite://')
    database.create_tables()
    
    user = User(name = 'Hello World')
    database.session.add_then_commit(user)
    
    user = database.session.query(User).get(1)
    print 'My name is', user.name
