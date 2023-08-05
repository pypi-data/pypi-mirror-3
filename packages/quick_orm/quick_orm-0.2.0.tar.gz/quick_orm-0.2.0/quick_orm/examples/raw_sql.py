from quick_orm.core import Database
from sqlalchemy import Column, String

__metaclass__ = Database.DefaultMeta

class User:
    name = Column(String(70))

if __name__ == '__main__':
    database = Database('sqlite://')
    database.create_tables()
    
    user = User(name = 'Tyler Long')
    database.session.add_then_commit(user)
    
    name = database.engine.execute('select name from user').scalar()
    print 'My name is', name
