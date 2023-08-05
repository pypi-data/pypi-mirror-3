from quick_orm.core import Database
from sqlalchemy import Column, String

class User(object):
    __metaclass__ = Database.DefaultMeta
    name = Column(String(30))

if __name__ == '__main__':
    database1 = Database('sqlite://')
    database1.create_tables()

    database2 = Database('sqlite://')
    database2.create_tables()
    
    user1 = User(name = 'user in database1')
    user2 = User(name = 'user in database2')
    database1.session.add_then_commit(user1)
    database2.session.add_then_commit(user2)
    
    print 'I am', database1.session.query(User).get(1).name
    print 'I am', database2.session.query(User).get(1).name
