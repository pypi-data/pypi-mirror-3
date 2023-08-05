from quick_orm.core import Database
from sqlalchemy import Column, String

class User(object):
    __metaclass__ = Database.DefaultMeta
    name = Column(String(70))

if __name__ == '__main__':
    database = Database('sqlite://')
    database.create_tables()
    
    count = database.engine.execute('select count(name) from user').scalar()
    print 'There are {0} users in total'.format(count)
