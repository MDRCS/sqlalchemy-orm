from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, Numeric, String, Boolean

Base = declarative_base()

"""
    :sqlalchemy-orm steps create a table:
    1- Create an instance of the declarative_base.
    2- Inherit from the Base.
    3- Define the table name.
    4- Define an attribute and set it to be a primary key.
"""


class Cookie(Base):
    __tablename__ = 'cookies'

    cookie_id = Column(Integer(), primary_key=True)
    cookie_name = Column(String(50), index=True)
    cookie_recipe_url = Column(String(255))
    cookie_sku = Column(String(55))
    quantity = Column(Integer())
    unit_cost = Column(Numeric(12, 2))

    def __init__(self, name, recipe_url=None, sku=None, quantity=0, unit_cost=0.00):
        self.cookie_name = name
        self.cookie_recipe_url = recipe_url
        self.cookie_sku = sku
        self.quantity = quantity
        self.unit_cost = unit_cost

    def __repr__(self):
        return "Cookie(cookie_name='{self.cookie_name}', " \
               "cookie_recipe_url='{self.cookie_recipe_url}', " \
               "cookie_sku='{self.cookie_sku}', " \
               "quantity={self.quantity}, " \
               "unit_cost={self.unit_cost})".format(self=self)


print(Cookie.__table__)

from datetime import datetime
from sqlalchemy import DateTime

"""
    1- Here we are making this column required (nullable=False) and requiring the values to be unique.
    2- The default sets this column to the current time if a date isn’t specified.
    3- Using onupdate here will reset this column to the current time every time any part of the record is updated.
"""


class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer(), primary_key=True)
    username = Column(String(15), nullable=False, unique=True)
    email_address = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    password = Column(String(25), nullable=False)
    created_on = Column(DateTime(), default=datetime.now)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)

    def __init__(self, username, email_address, phone, password):
        self.username = username
        self.email_address = email_address
        self.phone = phone
        self.password = password

    def __repr__(self):
        return "User(username='{self.username}', " \
               "email_address='{self.email_address}', " \
               "phone='{self.phone}', " \
               "password='{self.password}')".format(self=self)


print(User.__table__)

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref

"""
    Notice how we import the relationship and backref methods from sqlalchemy.orm.
    We are defining a ForeignKey just as we did with SQLAlchemy Core.
    This establishes a one-to-many relationship.

"""


class Order(Base):
    __tablename__ = 'orders'
    order_id = Column(Integer(), primary_key=True)
    user_id = Column(Integer(), ForeignKey('users.user_id'))
    shipped = Column(Boolean(), default=False)
    user = relationship("User", backref=backref('orders', order_by=order_id))

    def __repr__(self):
        return "Order(user_id={self.user_id}, " \
               "shipped={self.shipped})".format(self=self)


"""
    :the LineItem class has a one-to-one relationship with the Cookie class.
    The uselist=False keyword argument defines it as a one-to-one relationship.
    We also use a simpler back reference, as we do not care to control the order.
"""


class LineItems(Base):
    __tablename__ = 'line_items'
    line_items_id = Column(Integer(), primary_key=True)
    order_id = Column(Integer(), ForeignKey('orders.order_id'))
    cookie_id = Column(Integer(), ForeignKey('cookies.cookie_id'))
    quantity = Column(Integer())
    extended_cost = Column(Numeric(12, 2))
    order = relationship("Order", backref=backref('line_items', order_by=line_items_id))
    cookie = relationship("Cookie", uselist=False)

    """
        A __repr__ method defines how the object should be represented.
        It typically is the constructor call required to re-create the instance.
        This will show up later in our print output.
        Creates the tables in the database defined by the engine.

    """

    def __repr__(self):
        return "LineItems(order_id={self.order_id}, " \
               "cookie_id={self.cookie_id}, " \
               "quantity={self.quantity}, " \
               "extended_cost={self.extended_cost})".format(
            self=self)


from sqlalchemy import create_engine

engine = create_engine('sqlite:///:memory:')
Base.metadata.create_all(engine)

"""
    :The SQLAlchemy Session - States
    When we use a query to get an object, we get back an object that is connected to a session.
    That object could move through several states in relationship to the session.

    `Session States`

    Understanding the session states can be useful for troubleshooting exceptions and handling unexpected behaviors.
    There are four possible states for data object instances:

    `Transient`
    The instance is not in session, and is not in the database.

    `Pending`
    The instance has been added to the session with add(), but hasn’t been flushed or committed.

    `Persistent`
    The object in session has a corresponding record in the database.

    `Detached`
    The instance is no longer connected to the session, but has a record in the database.
    We can watch an instance move through these states as we work with it. We’ll start by creating an instance of a cookie.

"""

engine = create_engine('sqlite:///:memory:', echo=False)
Session = sessionmaker(bind=engine)

session = Session()

# in-memory db is db that works on the ram
# That is why each time we should create the tables
Base.metadata.create_all(engine)

cc_cookie = Cookie('chocolate chip',
                   'http://some.aweso.me/cookie/recipe.html',
                   'CC01', 12, 0.50)

from sqlalchemy import inspect

insp = inspect(cc_cookie)
print('\n')
# Transient
for state in ['transient', 'pending', 'persistent', 'detached']:
    print('{:>10}: {}'.format(state, getattr(insp, state)))

session.add(cc_cookie)
print('\n')
# pending
for state in ['transient', 'pending', 'persistent', 'detached']:
    print('{:>10}: {}'.format(state, getattr(insp, state)))

session.commit()
print('\n')
# persistent
for state in ['transient', 'pending', 'persistent', 'detached']:
    print('{:>10}: {}'.format(state, getattr(insp, state)))

session.expunge(cc_cookie)
print('\n')
# detached
for state in ['transient', 'pending', 'persistent', 'detached']:
    print('{:>10}: {}'.format(state, getattr(insp, state)))

# Changes History

session.add(cc_cookie)
cc_cookie.cookie_name = 'Change chocolate chip'

print(insp.modified)

for attr, attr_state in insp.attrs.items():
    if attr_state.history.has_changes():
        print('{}: {}'.format(attr, attr_state.value))
        print('History: {}\n'.format(attr_state.history))

"""
    So far, we have been using and joining different tables in our queries.
    However, what if we have a self-referential table (reflexive relationship) like a table of managers and their reports?
    The ORM allows us to establish a relationship that points to the same table; however,
    we need to specify an option called remote_side to make the relationship a many to one.
"""

# Exceptions - MultipleResultsFound, DetachedInstanceError

# the exception has occurred. In this case, it is because our query returned two rows and we told it to return one
# and only one.

dcc = Cookie('dark chocolate chip',
             'http://some.aweso.me/cookie/recipe_dark.html',
             'CC02', 1, 0.75)
session.add(dcc)
session.commit()

# results = session.query(Cookie).one()

from sqlalchemy.orm.exc import MultipleResultsFound

try:
    results = session.query(Cookie).one()
except MultipleResultsFound as exc:
    print('Exception: We found too many cookies... is that even possible?')

"""
    DetachedInstanceError
    This exception occurs when we attempt to access an attribute on an instance that needs
    to be loaded from the database, but the instance we are using is not currently attached to the database.
    Before we can explore this exception, we need to set up the records we are going to operate on.
"""

cookiemon = User('cookiemon', 'mon@cookie.com', '111-111-1111', 'password')
session.add(cookiemon)
o1 = Order()
o1.user = cookiemon
session.add(o1)

cc = session.query(Cookie).filter(Cookie.cookie_name ==
                                  "Change chocolate chip").one()
line1 = LineItems(order=o1, cookie=cc, quantity=2, extended_cost=1.00)

session.add(line1)
session.commit()

order = session.query(Order).first()
session.expunge(order)
# order.line_items.all()

from sqlalchemy.exc import IntegrityError

try:
    cookiemon = User('cookiemon', 'mon@cookie.com', '111-111-1111', 'password')
    session.add(cookiemon)
    o1 = Order()
    o1.user = cookiemon
    session.add(o1)

    cc = session.query(Cookie).filter(Cookie.cookie_name ==
                                      "Change chocolate chip").one()
    line1 = LineItems(order=o1, cookie=cc, quantity=2, extended_cost=1.00)

    session.add(line1)
    session.commit()
except IntegrityError as error:
    print("Error")
    # print('ERROR: {}'.format(error.orig.message))
    # session.rollback()

# Transactions


# print(print(session.query(Cookie.cookie_name, Cookie.quantity).all()))

from sqlalchemy.exc import IntegrityError


def ship_it(order_id):
    order = session.query(Order).get(order_id)
    for li in order.line_items:
        li.cookie.quantity = li.cookie.quantity - li.quantity
        session.add(li.cookie)
    order.shipped = True
    session.add(order)
    try:
        session.commit()
        print("shipped order ID: {}".format(order_id))
    except IntegrityError as error:
        print('ERROR: {!s}'.format(error.orig))
        session.rollback()


# print(ship_it(2))


class Employee(Base):
    __tablename__ = 'employees'

    id = Column(Integer(), primary_key=True)
    manager_id = Column(Integer(), ForeignKey('employees.id'))
    name = Column(String(255), nullable=False)

    manager = relationship("Employee", backref=backref('reports'), remote_side=[id])


Base.metadata.create_all(engine)
