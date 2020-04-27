from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, Numeric, String, Boolean

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
    So far, we have been using and joining different tables in our queries.
    However, what if we have a self-referential table (reflexive relationship) like a table of managers and their reports?
    The ORM allows us to establish a relationship that points to the same table; however,
    we need to specify an option called remote_side to make the relationship a many to one.
"""


class Employee(Base):
    __tablename__ = 'employees'

    id = Column(Integer(), primary_key=True)
    manager_id = Column(Integer(), ForeignKey('employees.id'))
    name = Column(String(255), nullable=False)

    manager = relationship("Employee", backref=backref('reports'), remote_side=[id])


Base.metadata.create_all(engine)
