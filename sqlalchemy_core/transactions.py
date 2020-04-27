from sqlalchemy import MetaData, create_engine


engine = create_engine('sqlite:///cookies_trans.db')
metadata = MetaData()

"""
    There is already a good example of when we might want to do this in our existing database.
    After a customer has ordered cookies from us, we need to ship those cookies
    to the customer and remove them from our inventory.
    However, what if we do not have enough of the right cookies to fulfill an order?
    We will need to detect that and not ship that order. We can solve this with transactions.

"""

from datetime import datetime

from sqlalchemy import (MetaData, Table, Column, Integer, Numeric, String,
                        DateTime, ForeignKey, Boolean, create_engine, CheckConstraint)

metadata = MetaData()

cookies = Table('cookies', metadata,
                Column('cookie_id', Integer(), primary_key=True),
                Column('cookie_name', String(50), index=True),
                Column('cookie_recipe_url', String(255)),
                Column('cookie_sku', String(55)),
                Column('quantity', Integer()),
                Column('unit_cost', Numeric(12, 2)),
                CheckConstraint('quantity >= 0', name='quantity_positive')
                )

users = Table('users', metadata,
              Column('user_id', Integer(), primary_key=True),
              Column('username', String(15), nullable=False, unique=True),
              Column('email_address', String(255), nullable=False),
              Column('phone', String(20), nullable=False),
              Column('password', String(25), nullable=False),
              Column('created_on', DateTime(), default=datetime.now),
              Column('updated_on', DateTime(), default=datetime.now, onupdate=datetime.now)
              )

orders = Table('orders', metadata,
               Column('order_id', Integer()),
               Column('user_id', ForeignKey('users.user_id')),
               Column('shipped', Boolean(), default=False)
               )

line_items = Table('line_items', metadata,
                   Column('line_items_id', Integer(), primary_key=True),
                   Column('order_id', ForeignKey('orders.order_id')),
                   Column('cookie_id', ForeignKey('cookies.cookie_id')),
                   Column('quantity', Integer()),
                   Column('extended_cost', Numeric(12, 2))
                   )

# metadata.create_all(engine)
connection = engine.connect()

from sqlalchemy import select, insert, update

ins = insert(users).values(
    username="cookiemon",
    email_address="mon@cookie.com",
    phone="111-111-1111",
    password="password"
)
# result = connection.execute(ins)

ins = cookies.insert()
inventory_list = [
    {
        'cookie_name': 'chocolate chip',
        'cookie_recipe_url': 'http://some.aweso.me/cookie/recipe.html',
        'cookie_sku': 'CC01',
        'quantity': '12',
        'unit_cost': '0.50'
    },
    {
        'cookie_name': 'dark chocolate chip',
        'cookie_recipe_url': 'http://some.aweso.me/cookie/recipe_dark.html',
        'cookie_sku': 'CC02',
        'quantity': '1',
        'unit_cost': '0.75'
    }
]
# result = connection.execute(ins, inventory_list)

ins = insert(orders).values(user_id=1, order_id=1)
# result = connection.execute(ins)
ins = insert(line_items)
order_items = [
    {
        'order_id': 1,
        'cookie_id': 1,
        'quantity': 9,
        'extended_cost': 4.50
    }
]
# result = connection.execute(ins, order_items)

ins = insert(orders).values(user_id=1, order_id=2)
# result = connection.execute(ins)

ins = insert(line_items)
order_items = [
    {
        'order_id': 2,
        'cookie_id': 2,
        'quantity': 1,
        'extended_cost': 1.50
    },
    {
        'order_id': 2,
        'cookie_id': 1,
        'quantity': 4,
        'extended_cost': 4.50
    }
]

# result = connection.execute(ins, order_items)


from sqlalchemy.exc import IntegrityError


# transaction handle the statements in `all or nothing` way if all statements are valid
# the query will be `commited` else rollback return the problem where it's

def ship_it(order_id):
    s = select([line_items.c.cookie_id, line_items.c.quantity])
    s = s.where(line_items.c.order_id == order_id)
    # Transaction
    transaction = connection.begin()
    cookies_to_ship = connection.execute(s).fetchall()
    try:
        for cookie in cookies_to_ship:
            u = update(cookies).where(cookies.c.cookie_id == cookie.cookie_id)
            u = u.values(quantity=cookies.c.quantity - cookie.quantity)
            result = connection.execute(u)
        u = update(orders).where(orders.c.order_id == order_id)
        u = u.values(shipped=True)
        result = connection.execute(u)
        print("Shipped order ID: {}".format(order_id))
        transaction.commit()
    except IntegrityError as error:
        transaction.rollback()
        print(error)


print(ship_it(1))

"""
    We can see that we don’t have enough cookies in our inventory to fulfill the second order;
    however, in our fast-paced warehouse, these orders might be processed at the same time.
    Now try shipping our second order with the ship_it function

"""

s = select([cookies.c.cookie_name, cookies.c.quantity])
results = connection.execute(s).fetchall()

for r in results:
    print(r)
