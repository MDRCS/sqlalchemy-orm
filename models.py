from sqlalchemy import Integer, MetaData, String, Numeric, DateTime, Table, Column, ForeignKey, BOOLEAN, create_engine
from datetime import datetime

engine = create_engine('sqlite:///cookies.db')
metadata = MetaData()

"""
    Model: Cookies delivery Service

        + Users
            user_id
            customer_number
            username
            email_address
            phone
            password
            created_on
            updated_on

        + Orders
            order_id
            user_id

        + Line-items
            order_id
            cookie_id
            quantity
            extended_cost

        + Cookies
            cookie_id
            cookie_name
            cookie_recipe_url
            cookie_sku
            quantity
            unit_cost
"""

users = Table('users', metadata,
              Column('user_id', Integer(), primary_key=True),
              Column('username', String(15), nullable=False, unique=True),
              Column('email_address', String(255), nullable=False),
              Column('phone', String(20), nullable=False),
              Column('password', String(25), nullable=False),
              Column('created_on', DateTime(), default=datetime.now),
              Column('updated_on', DateTime(), default=datetime.now, onupdate=datetime.now)
              )

cookies = Table('cookies', metadata,
                Column('cookie_id', Integer(), primary_key=True),
                Column('cookie_name', String(50), index=True),
                Column('cookie_recipe_url', String(255)),
                Column('cookie_sku', String(55)),
                Column('quantity', Integer()),
                Column('unit_cost', Numeric(12, 2))
                )

orders = Table('orders', metadata,
               Column('order_id', Integer(), primary_key=True),
               Column('user_id', ForeignKey('users.user_id')),
               )

line_items = Table('line_items', metadata,
                   Column('line_items_id', Integer(), primary_key=True),
                   Column('order_id', ForeignKey('orders.order_id')),
                   Column('cookie_id', ForeignKey('cookies.cookie_id')),
                   Column('quantity', Integer()),
                   Column('extended_cost', Numeric(12, 2))
                   )

"""
    Notice that we used a string instead of an actual reference to the column.
    Using strings instead of an actual column allows us to separate the table definitions across multiple modules and/or
    not have to worry about the order in which our tables are loaded.
    This is because SQLAlchemy will only perform the resolution of that string to a table name and column the first time it is accessed.
    If we use hard references, such as cookies.c.cookie_id, in our ForeignKey definitions it will perform that resolution during module
    initialization and could fail depending on the order in which the tables are loaded.”

    -> best practices ForeignKey('orders.order_id') instead of ForeignKey(orders.c.order_id) !! dangerous
"""

# Define Foreign key explicitly
# order_id = ForeignKeyConstraint(['order_id'], ['orders.order_id'])

# create all tables and columns defined above
metadata.create_all(engine)
