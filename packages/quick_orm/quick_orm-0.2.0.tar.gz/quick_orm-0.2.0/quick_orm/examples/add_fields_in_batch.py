from quick_orm.core import Database
from sqlalchemy import Column, String, DateTime, func

class DefaultModel(object):
    name = Column(String(70))
    created = Column(DateTime, default = func.now(), nullable = False)

__metaclass__ = Database.MetaBuilder(DefaultModel)

class User:
    """Define __metaclass__ here to override the global one"""

class Group:
    """Define __metaclass__ here to override the global one"""
   

if __name__ == '__main__':
    database = Database('sqlite://')
    database.create_tables()
    user = User(name = 'tylerlong')
    database.session.add(user)
    group = Group(name = 'python')
    database.session.add_then_commit(group)

    print user.name, user.created
    print group.name, group.created
