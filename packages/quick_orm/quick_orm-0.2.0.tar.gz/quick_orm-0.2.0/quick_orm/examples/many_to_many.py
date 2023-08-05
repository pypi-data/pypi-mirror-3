from quick_orm.core import Database
from sqlalchemy import Column, String, Text

__metaclass__ = Database.DefaultMeta

@Database.many_to_many('role')
class User:
    name = Column(String(70))

class Role:
    name = Column(String(70))


if __name__ == '__main__':
    database = Database('sqlite://')
    database.create_tables()
    
    user1 = User(name = 'Tyler Long')
    database.session.add(user1)
    user2 = User(name = 'Peter Lau')
    database.session.add(user1)
    role = Role(name = 'Administrator', users = [user1, user2])
    database.session.add_then_commit(role)

    admin_role = database.session.query(Role).filter_by(name = 'Administrator').one()
    print ', '.join([user.name for user in admin_role.users]), 'are admintrators'
