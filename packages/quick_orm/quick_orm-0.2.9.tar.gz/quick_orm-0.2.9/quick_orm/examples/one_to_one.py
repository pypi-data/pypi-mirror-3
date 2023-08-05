from quick_orm.core import Database
from sqlalchemy import Column, String

class User(object):
    __metaclass__ = Database.DefaultMeta
    name = Column(String(30))

@Database.foreign_key(User, one_to_one = True)
class Contact(object):
    __metaclass__ = Database.DefaultMeta
    email = Column(String(70))
    address = Column(String(70))

if __name__ == '__main__':
    db = Database('sqlite://')
    db.create_tables()

    contact = Contact(email = 'quick.orm.feedback@gmail.com', address = 'Shenzhen, China')
    user = User(name = 'Tyler Long', contact = contact)
    db.session.add_then_commit(user)
    
    user = db.session.query(User).get(1)
    print 'User:', user.name
    print 'Email:', user.contact.email
    print 'Address:', user.contact.address
