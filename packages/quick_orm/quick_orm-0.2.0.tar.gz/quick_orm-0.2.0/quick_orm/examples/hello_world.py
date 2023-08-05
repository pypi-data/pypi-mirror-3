from quick_orm.core import Database
from sqlalchemy import Column, String

__metaclass__ = Database.DefaultMeta

class User:
    name = Column(String(70))

if __name__ == '__main__':
    database = Database('sqlite://')
    database.create_tables()
    
    user1 = User(name = 'Hello World')
    database.session.add_then_commit(user1)
    
    user = database.session.query(User).get(1)
    print 'My name is', user.name
