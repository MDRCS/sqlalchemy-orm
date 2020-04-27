from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_orm.models import User, Cookie, LineItems, Order, Base, Employee

"""
    The Session
    The session is the way SQLAlchemy ORM interacts with the database. It wraps a database connection via an engine,
    and provides an identity map for objects that you load via the session or associate with the session.
    The identity map is a cache-like data structure that contains a unique list of objects determined
    by the object’s table and primary key. A session also wraps a transaction, and that transaction will be open until
    the session is committed or rolled back, very similar to the process described in “Transactions”.

    To create a new session, SQLAlchemy provides the sessionmaker class to ensure that sessions can be created
    with the same parameters throughout an application.It does this by creating a Session class that has been configured
    according to the arguments passed to the sessionmaker factory. The sessionmaker factory should be used just
    once in your application global scope, and treated like a configuration setting.
    Let’s create a new session associated with an in-memory SQLite database:

    1- Imports the sessionmaker class.
    2- Defines a Session class with the bind configuration supplied by sessionmaker.
    3- Creates a session for our use from our generated Session class.

"""

"""
    :NOTE
    If you want to see the details of what is happening here, you can add echo=True to your create_engine statement
    as a keyword argument after the connection string. Make sure to only do this for testing,
    and don’t use echo=True in production!

"""

engine = create_engine('sqlite:///:memory:', echo=False)
Session = sessionmaker(bind=engine)

session = Session()

# in-memory db is db that works on the ram
# That is why each time we should create the tables
Base.metadata.create_all(engine)

cc_cookie = Cookie(cookie_name='chocolate chip',
                   cookie_recipe_url='http://some.aweso.me/cookie/recipe.html',
                   cookie_sku='CC01',
                   quantity=12,
                   unit_cost=0.50)

# Creating an instance of the Cookie class.
# Adding the instance to the session.
# Committing the session.

session.add(cc_cookie)
session.commit()

print(cc_cookie.cookie_id)

dcc = Cookie(cookie_name='dark chocolate chip',
             cookie_recipe_url='http://some.aweso.me/cookie/recipe_dark.html',
             cookie_sku='CC02',
             quantity=1,
             unit_cost=0.75)
mol = Cookie(cookie_name='molasses',
             cookie_recipe_url='http://some.aweso.me/cookie/recipe_molasses.html',
             cookie_sku='MOL01',
             quantity=1,
             unit_cost=0.80)

"""
    Notice that we used the flush() method on the session instead of commit() in Example below.
    A flush is like a commit; however, it doesn’t perform a database commit and end the transaction.

    Because of this, the dcc and mol instances are still connected to the session,
    and can be used to perform additional database tasks without triggering additional database queries.
    We also issue the session.flush() statement one time, even though we added multiple records into the database.
    This actually results in two insert statements being sent to the database inside a single transaction.

"""

session.add(dcc)
session.add(mol)
session.flush()

c1 = Cookie(cookie_name='peanut butter',
            cookie_recipe_url='http://some.aweso.me/cookie/peanut.html',
            cookie_sku='PB01',
            quantity=24,
            unit_cost=0.25)
c2 = Cookie(cookie_name='oatmeal raisin',
            cookie_recipe_url='http://some.okay.me/cookie/raisin.html',
            cookie_sku='EWW01',
            quantity=100,
            unit_cost=1.00)

session.bulk_save_objects([c1, c2])
session.commit()

# c1 isn't associated with session
# c1.cookie_id -> none
print(c1.cookie_id)

"""
    will not result in anything being printed to the screen because the c1 object isn’t associated with the session,
    and can’t refresh its cookie_id for printing. If we look at what was sent to the database,
    we can see only a single insert statement was in the transaction:

    INFO:sqlalchemy.engine.base.Engine:INSERT INTO cookies (cookie_name,
    cookie_recipe_url, cookie_sku, quantity, unit_cost) VALUES (?, ?, ?, ?, ?)

    INFO:sqlalchemy.engine.base.Engine:(
    ('peanut butter', 'http://some.aweso.me/cookie/peanut.html', 'PB01', 24, 0.25),
    ('oatmeal raisin', 'http://some.okay.me/cookie/raisin.html', 'EWW01', 100, 1.0))
    INFO:sqlalchemy.engine.base.Engine:COMMIT”

"""

"""
    The method (two inserts with flush) is substantially faster than performing multiple individual adds and inserts as we did in the bulk save.
    This speed does come at the expense of some features we get in the normal add and commit, such as:

    1- Relationship settings and actions are not respected or triggered.
    2- The objects are not connected to the session.
    3- Fetching primary keys is not done by default.
    4- No events will be triggered.
    In addition to bulk_save_objects, there are additional methods to create and update objects via a dictionary,
    and you can learn more about bulk operations and their performance in the SQLAlchemy documentation.”

    :TIP
    If you are inserting multiple records and don’t need access to relationships or the inserted primary key,
    use bulk_save_objects or its related methods. This is especially true if you are ingesting data from an external
    data source such as a CSV or a large JSON document with nested arrays.

"""

cookies = session.query(Cookie).all()
print(cookies)

"""
    Because the returned value is a list of objects, we can use those objects as we would normally.
    These objects are connected to the session, which means we can change them or delete them and persist
    that change to the database as shown later in this chapter.
"""

for cookie in session.query(Cookie):
    print(cookie)

"""
    We don’t append an all() when using an iterable.
    Using the iterable approach allows us to interact with each record object individually,
    release it, and get the next object.
"""

"""
    :TIPS FOR GOOD PRODUCTION CODE
    When writing production code, you should follow these guidelines:
    Use the iterable version of the query over the all() method. It is more memory efficient than handling
    a full list of objects and we tend to operate on the data one record at a time anyway.
    To get a single record, use the first() method (rather than one() or scalar()) because it is clearer to our fellow coders.
    The only exception to this is when you must ensure that there is one and only one result from a query; in that case, use one().
    Use the scalar() method sparingly, as it raises errors if a query ever returns more than one row with one column.
    In a query that selects entire records, it will return the entire record object, which can be confusing and cause errors.”

"""

print(session.query(Cookie.cookie_name, Cookie.quantity).first())

# Ordering

from sqlalchemy import desc

for cookie in session.query(Cookie).order_by(Cookie.quantity):
    print('{:3} - {}'.format(cookie.quantity, cookie.cookie_name))

for cookie in session.query(Cookie).order_by(desc(Cookie.quantity)):
    print('{:3} - {}'.format(cookie.quantity, cookie.cookie_name))

"""
    NOTE
    The desc() function can also be used as a method on a column object,
    such as Cookie.quantity.desc(). However, that can be a bit more confusing to read in long statements,
    and so I always use desc() as a function.
"""

# limiting

# inefficient way to get data
query = session.query(Cookie).order_by(Cookie.quantity)[:2]
print([result.cookie_name for result in query])

# efficient and best practices way of limiting results
query = session.query(Cookie).order_by(Cookie.quantity).limit(2)
print([result.cookie_name for result in query])

# Built-in sql func: SUM, COUNT

# Notice the use of scalar, which will return only the leftmost column in the first record.

from sqlalchemy import func

inv_count = session.query(func.sum(Cookie.quantity)).scalar()
print(inv_count)

rec_count = session.query(func.count(Cookie.cookie_name)).first()
print(rec_count)

# labeling
rec_count = session.query(func.count(Cookie.cookie_name) \
                          .label('inventory_count')).first()

print(rec_count.keys())
print(rec_count.inventory_count)

# Filtering
record = session.query(Cookie).filter(Cookie.cookie_name == 'chocolate chip').first()
print(record)

record = session.query(Cookie).filter_by(cookie_name='chocolate chip').first()
print(record)

query = session.query(Cookie).filter(Cookie.cookie_name.like('%chocolate%'))
for record in query:
    print(record.cookie_name)

results = session.query(Cookie.cookie_name, 'SKU-' + Cookie.cookie_sku).all()
for row in results:
    print(row)

from sqlalchemy import cast, Numeric

query = session.query(Cookie.cookie_name,
                      cast((Cookie.quantity * Cookie.unit_cost),
                           Numeric(12, 2)).label('inv_cost'))
for result in query:
    print('{} - {}'.format(result.cookie_name, result.inv_cost))

from sqlalchemy import and_, or_, not_

query = session.query(Cookie).filter(
    Cookie.quantity > 23,
    Cookie.unit_cost < 0.40
)
for result in query:
    print(result.cookie_name)

from sqlalchemy import and_, or_, not_

query = session.query(Cookie).filter(
    or_(
        Cookie.quantity.between(10, 50),
        Cookie.cookie_name.contains('chip')
    )
)
for result in query:
    print(result.cookie_name)

# Updating

"""
    We’re querying to get the object here; however, if you already have it, you can directly edit it without querying it again.
"""

query = session.query(Cookie)
cc_cookie = query.filter(Cookie.cookie_name == "chocolate chip").first()
cc_cookie.quantity = cc_cookie.quantity + 120
session.commit()
print(cc_cookie.quantity)

query = session.query(Cookie)
query = query.filter(Cookie.cookie_name == "chocolate chip")
query.update({Cookie.quantity: Cookie.quantity - 20})

cc_cookie = query.first()
print(cc_cookie.quantity)

# Deleting

query = session.query(Cookie)
query = query.filter(Cookie.cookie_name == "dark chocolate chip")
dcc_cookie = query.one()
session.delete(dcc_cookie)
session.commit()
dcc_cookie = query.first()
print(dcc_cookie)

query = session.query(Cookie)
query = query.filter(Cookie.cookie_name == "molasses")
query.delete()
mol_cookie = query.first()
print(mol_cookie)

# Relationships

cookiemon = User(username='cookiemon',
                 email_address='mon@cookie.com',
                 phone='111-111-1111',
                 password='password')
cakeeater = User(username='cakeeater',
                 email_address='cakeeater@cake.com',
                 phone='222-222-2222',
                 password='password')
pieperson = User(username='pieperson',
                 email_address='person@pie.com',
                 phone='333-333-3333',
                 password='password')

session.add(cookiemon)
session.add(cakeeater)
session.add(pieperson)
session.commit()

"""

    :Process
    In Example, we create an empty Order instance, and set its user property to the cookiemon instance.
    Next, we add it to the session. Then we query for the chocolate chip cookie and create a LineItem,
    and set the cookie to be the chocolate chip one we just queried for.
    We repeat that process for the second line item on the order; however, we build it up piecemeal.
    Finally, we add the line items to the order and commit it.”

"""

o1 = Order()
o1.user = cookiemon
session.add(o1)

cc = session.query(Cookie).filter(Cookie.cookie_name ==
                                  "chocolate chip").one()
line1 = LineItems(cookie=cc, quantity=2, extended_cost=1.00)

pb = session.query(Cookie).filter(Cookie.cookie_name ==
                                  "peanut butter").one()
line2 = LineItems(quantity=12, extended_cost=3.00)
line2.cookie = pb
line2.order = o1

o1.line_items.append(line1)
o1.line_items.append(line2)
session.commit()

o2 = Order()
o2.user = cakeeater

cc = session.query(Cookie).filter(Cookie.cookie_name ==
                                  "chocolate chip").one()
line1 = LineItems(cookie=cc, quantity=24, extended_cost=12.00)

oat = session.query(Cookie).filter(Cookie.cookie_name ==
                                   "oatmeal raisin").one()
line2 = LineItems(cookie=oat, quantity=6, extended_cost=6.00)

o2.line_items.append(line1)
o2.line_items.append(line2)

session.add(o2)
session.commit()

# Joins

query = session.query(Order.order_id, User.username, User.phone,
                      Cookie.cookie_name, LineItems.quantity,
                      LineItems.extended_cost)

query = query.join(User).join(LineItems).join(Cookie)
results = query.filter(User.username == 'cookiemon').all()
print(results)

# Difference between join and outerjoin is that join will give us count only for users that made orders

query = session.query(User.username, func.count(Order.order_id))
query = query.outerjoin(Order).group_by(User.username)
for row in query:
    print(row)

# Employee Table - Reflexive Relation

Base.metadata.create_all(engine)

marsha = Employee(name='Marsha')
fred = Employee(name='Fred')
marsha.reports.append(fred)
session.add(marsha)
session.commit()

# Display managers of marsha

for report in marsha.reports:
    print(report.name)

# Grouping

query = session.query(User.username, func.count(Order.order_id))
query = query.outerjoin(Order).group_by(User.username)
for row in query:
    print(row)


# Chaining - Encapsulate Ops into func
def get_orders_by_customer(cust_name):
    query = session.query(Order.order_id, User.username, User.phone,
                          Cookie.cookie_name, LineItems.quantity,
                          LineItems.extended_cost)
    query = query.join(User).join(LineItems).join(Cookie)
    results = query.filter(User.username == cust_name).all()
    return results


get_orders_by_customer('cakeeater')


def get_orders_by_customer(cust_name, shipped=None, details=False):
    query = session.query(Order.order_id, User.username, User.phone)
    query = query.join(User)
    if details:
        query = query.add_columns(Cookie.cookie_name, LineItems.quantity,
                                  LineItems.extended_cost)
        query = query.join(LineItems).join(Cookie)
    if shipped is not None:
        query = query.filter(Order.shipped == shipped)
    results = query.filter(User.username == cust_name).all()
    return results


print(get_orders_by_customer('cakeeater'))

print(get_orders_by_customer('cakeeater', details=True))

print(get_orders_by_customer('cakeeater', shipped=True))

print(get_orders_by_customer('cakeeater', shipped=False))

print(get_orders_by_customer('cakeeater', shipped=False, details=True))


# Raw Queries
from sqlalchemy import text
query = session.query(User).filter(text("username='cookiemon'"))
print(query.all())
