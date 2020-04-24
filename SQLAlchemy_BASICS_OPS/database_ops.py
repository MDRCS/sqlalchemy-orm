from models import cookies, users, line_items, orders, engine
from sqlalchemy import insert, select

conn = engine.connect()

ins = cookies.insert().values(
    cookie_name="chocolate chip",
    cookie_recipe_url="http://some.aweso.me/cookie/recipe.html",
    cookie_sku="CC01",
    quantity="12",
    unit_cost="0.50"
)

# Persist the parameters and give us the sql query for the insertion
print(str(ins))

# This command will compile the insertion query show us params and values of cookies's table
print(ins.compile().params)

# Execute allows us to send query and execute it in the database
# result = conn.execute(ins)

# Get the primary key of the record that we inserted
# print(result.inserted_primary_key)

"""
    In addition to having insert as an instance method off a Table object, it is also available as a top-level function
    for those times that you want to build a statement “generatively” (a step at a time) or when the table may not be
    initially known. For example, our company might run two separate divisions, each with its own separate inventory tables.
    Using the insert function shown in Example 2-3 would allow us to use one statement and just swap the tables.”
"""

ins = insert(cookies).values(
    cookie_name="chocolate chip",
    cookie_recipe_url="http://some.aweso.me/cookie/recipe.html",
    cookie_sku="CC01",
    quantity="12",
    unit_cost="0.50"
)

print(str(ins))

# result = conn.execute(ins, cookie_name='dark chocolate chip',
#                       cookie_recipe_url='http://some.aweso.me/cookie/recipe_dark.html',
#                       cookie_sku='CC02',
#                       quantity='1',
#                       unit_cost='0.75')

# print(result.inserted_primary_key)

"""
    Multiple Insert
"""

ins = cookies.insert()

inventory_list = [
    {
        'cookie_name': 'peanut butter',
        'cookie_recipe_url': 'http://some.aweso.me/cookie/peanut.html',
        'cookie_sku': 'PB01',
        'quantity': '24',
        'unit_cost': '0.25'
    },
    {
        'cookie_name': 'oatmeal raisin',
        'cookie_recipe_url': 'http://some.okay.me/cookie/raisin.html',
        'cookie_sku': 'EWW01',
        'quantity': '100',
        'unit_cost': '1.00'
    }
]

# result = conn.execute(ins, inventory_list)

"""
    Query Records in the database
"""

s = select([cookies])
print("sql query -> :", str(s))

ResultProxy = conn.execute(s)
results = ResultProxy.fetchall()

first_row = results[0]

print("cookie name : (by index -> 1)", first_row[1])
print("cookie name : (by name)", first_row.cookie_name)
print("cookie name : (by column object)", first_row[cookies.c.cookie_name])

"""
    :TIPS FOR GOOD PRODUCTION CODE
    |When writing production code, you should follow these guidelines:
    |Use the first method for getting a single record over both the fetchone and scalar methods,
    |because it is clearer to our fellow coders.
    |Use the iterable version of the ResultProxy over the fetchall and fetchone methods.
    |It is more memory efficient and we tend to operate on the data one record at a time.
    |Avoid the fetchone method, as it leaves connections open if you are not careful.
    |Use the scalar method sparingly, as it raises errors if a query ever returns more than one row with one column,
    |which often gets missed during testing.
"""

s = select([cookies.c.cookie_name, cookies.c.quantity])
rp = conn.execute(s)
print(rp.keys())
results = rp.fetchall()

"""
    “Order by quantity ascending”
"""

s = select([cookies.c.cookie_name, cookies.c.quantity])
s = s.order_by(cookies.c.quantity, cookies.c.cookie_name)
rp = conn.execute(s)
for cookie in rp:
    print('{} - {}'.format(cookie.quantity, cookie.cookie_name))

"""
    The desc() function can also be used as a method on a Column object, such as cookies.c.quantity.desc(). However,
    that can be a bit more confusing to read in long statements, so I always use desc() as a function.
"""

from sqlalchemy import desc

s = select([cookies.c.cookie_name, cookies.c.quantity])
s = s.order_by(desc(cookies.c.quantity))
rp = conn.execute(s)
for cookie in rp:
    print('{} - {}'.format(cookie.quantity, cookie.cookie_name))

# Limiting func

s = s.order_by(cookies.c.quantity)
s = s.limit(2)
rp = conn.execute(s)
print([result.cookie_name for result in rp])

"""
    Built-In SQL Functions and Labels: SUM(), COUNT() ..
"""

from sqlalchemy.sql import func

s = select([func.count(cookies.c.cookie_name)])
rp = conn.execute(s)
record = rp.first()
print(record.keys())
print(record.count_1)

"""
    Renaming our func count (to avoid shadowing others func in python)
"""

s = select([func.count(cookies.c.cookie_name).label('inventory_count')])
rp = conn.execute(s)
record = rp.first()
print(record.keys())
print(record.inventory_count)

"""
    Filtring queries (where clause)
"""

s = select([cookies]).where(cookies.c.cookie_name == 'chocolate chip')
rp = conn.execute(s)
record = rp.first()
print(record.items())

s = select([cookies]).where(cookies.c.cookie_name.like('%chocolate%')).where(cookies.c.quantity == 12)
rp = conn.execute(s)
for record in rp.fetchall():
    print(record.cookie_name)

"""
    Operators: (==, !=, <, >, <=, >=)
"""

# String concatenation with \+
s = select([cookies.c.cookie_name, 'SKU-' + cookies.c.cookie_sku])
for row in conn.execute(s):
    print(row)

from sqlalchemy import cast, Numeric

s = select([cookies.c.cookie_name, cast((cookies.c.quantity * cookies.c.unit_cost), Numeric(12, 2)).label('inv_cost')])
for row in conn.execute(s):
    print('{} - {}'.format(row.cookie_name, row.inv_cost))

"""

    Boolean Operators
    SQLAlchemy also allows for the SQL Boolean operators AND, OR, and NOT via the bitwise logical
    operators (&, |, and ~). Special care must be taken when using the AND, OR, and NOT overloads
    because of the Python operator precedence rules. For instance, & binds more closely than <,
    so when you write A < B & C < D, what you are actually writing is A < (B&C) < D,
    when you probably intended to get (A < B) & (C < D).
    Please use conjunctions instead of these overloads, as they will make your code more expressive.

"""

from sqlalchemy import and_, or_, not_

s = select([cookies]).where(and_(
    cookies.c.quantity > 23,
    cookies.c.unit_cost < 0.40
))

for row in conn.execute(s):
    print(row.cookie_name)

"""
    or operator: The or_() function works as the opposite of and_() and includes results that match either
                one of the supplied clauses.
                If we wanted to search our inventory for cookie types that we have between 10 and 50 of in stock
                or where the name contains chip.

"""

from sqlalchemy import and_, or_, not_

s = select([cookies]).where(or_(
    cookies.c.quantity.between(10, 50),
    cookies.c.cookie_name.contains('chip')
))

for row in conn.execute(s):
    print(row.cookie_name)

"""
    Updating Data
    Much like the insert method we used earlier, there is also an update method with syntax almost identical to inserts,
    except that it can specify a where clause that indicates which rows to update. Like insert statements,
    update statements can be created by either the update() function or the update() method on the table being updated.
    You can update all rows in a table by leaving off the where clause.

"""

from sqlalchemy import update

u = update(cookies).where(cookies.c.cookie_name == "chocolate chip")
u = u.values(quantity=(cookies.c.quantity + 120))
result = conn.execute(u)
print(result.rowcount)

"""

    Delete Operation
    Unlike insert() and update(), delete() takes no values parameter, only an optional where clause
    (omitting the where clause will delete all rows from the table).

"""

from sqlalchemy import delete

u = delete(cookies).where(cookies.c.cookie_name == "dark chocolate chip")
# result = conn.execute(u)
# print(result.rowcount)

s = select([cookies]).where(cookies.c.cookie_name == "dark chocolate chip")
# result = conn.execute(s).fetchall()
# print(len(result))

customer_list = [
    {
        'username': "cookiemon",
        'email_address': "mon@cookie.com",
        'phone': "111-111-1111",
        'password': "password"
    },
    {
        'username': "cakeeater",
        'email_address': "cakeeater@cake.com",
        'phone': "222-222-2222",
        'password': "password"
    },
    {
        'username': "pieguy",
        'email_address': "guy@pie.com",
        'phone': "333-333-3333",
        'password': "password"
    }
]

ins = users.insert()
# result = conn.execute(ins, customer_list)

ins = insert(orders).values(user_id=1, order_id=1)
# result = conn.execute(ins)

ins = insert(line_items)
order_items = [
    {
        'order_id': 1,
        'cookie_id': 1,
        'quantity': 2,
        'extended_cost': 1.00
    },
    {
        'order_id': 1,
        'cookie_id': 3,
        'quantity': 12,
        'extended_cost': 3.00
    }
]

result = conn.execute(ins, order_items)

ins = insert(orders).values(user_id=2, order_id=2)
# result = conn.execute(ins)

ins = insert(line_items)
order_items = [
    {
        'order_id': 2,
        'cookie_id': 1,
        'quantity': 24,
        'extended_cost': 12.00
    },
    {
        'order_id': 2,
        'cookie_id': 4,
        'quantity': 6,
        'extended_cost': 6.00
    }
]
# result = conn.execute(ins, order_items)
# print(result)

"""
    Joins:

    Now let’s use the join() and outerjoin() methods to
    take a look at how to query related data.

    For example, to fulfill the order placed by the cookiemon
    user, we need to determine how many of each
    cookie type were ordered. This requires you to use a
    total of three joins to get all the way down to the
    name of the cookies.

    :Query
    select users.username, cookies.cookie_name
    from users, cookies, orders, line_items
    WHERE users.username == "cookiemon"  and
          users.user_id == orders.user_id and
          orders.order_id == line_items.order_id and
          line_items.cookie_id == cookies.cookie_id

    The SQL Also could looks like this:
    SELECT orders.order_id, users.username, users.phone, cookies.cookie_name,
    line_items.quantity, line_items.extended_cost FROM users JOIN orders ON
    users.user_id = orders.user_id JOIN line_items ON orders.order_id =
    line_items.order_id JOIN cookies ON cookies.cookie_id = line_items.cookie_id
    WHERE users.username = :username_1

"""

columns = [orders.c.order_id, users.c.username, users.c.phone, cookies.c.cookie_name, line_items.c.quantity,
           line_items.c.extended_cost]
cookiemon_orders = select(columns)
cookiemon_orders = cookiemon_orders.select_from(users.join(orders).join(line_items).join(cookies)).where(
    users.c.username == 'cookiemon')
result = conn.execute(cookiemon_orders).fetchall()
for row in result:
    print(row)

"""
     Using outerjoin to select from multiple tables
"""

columns = [users.c.username, orders.c.order_id]
all_orders = select(columns)
all_orders = all_orders.select_from(users.outerjoin(orders))
result = conn.execute(all_orders).fetchall()
for row in result:
    print(row)

"""
    Other Methods to Express your query
"""

# Raw Queries
result = conn.execute("select * from orders").fetchall()
print(result)

from sqlalchemy import text

# Partial text query
stmt = select([users]).where(text('username="cookiemon"'))
print(conn.execute(stmt).fetchall())

"""
    :Aliases
    When using joins, it is often necessary to refer to a table more than once.
    In SQL, this is accomplished by using aliases in the query. For instance, suppose we have the following (partial)
    schema that tracks the reporting structure within an organization.

"""

from models import engine_emp, employees

conn1 = engine_emp.connect()
emp = insert(employees).values(
    manager_id=1,
    name="fred"
)

# result = conn1.execute(emp)
query = select([employees])
results = conn1.execute(query).fetchall()

for r in results:
    print(r)

"""

    Now suppose we want to select all the employees managed by an employee named Fred. In SQL, we might write the following:
    SELECT employee.name
    FROM employee, employee AS manager
    WHERE employee.manager_id = manager.id
    AND manager.name = 'Fred'

"""

manager = employees.alias('manager')
query = select([employees.c.name], and_(employees.c.manager_id == manager.c.id, manager.c.name == 'mdrahali'))
results = conn1.execute(query).fetchall()

for r in results:
    print(r)

"""
    :Grouping
    When using grouping, you need one or more columns to group on and one or more columns
    that it makes sense to aggregate with counts, sums, etc., as you would in normal SQL.

"""

columns = [users.c.username, func.count(orders.c.order_id)]
all_orders = select(columns)
all_orders = all_orders.select_from(users.outerjoin(orders))
all_orders = all_orders.group_by(users.c.username)
result = conn.execute(all_orders).fetchall()
for row in result:
    print(row)


def get_orders_by_customer(cust_name, shipped=False, details=False):
    columns = [orders.c.order_id, users.c.username, users.c.phone]
    joins = users.join(orders)
    if details:
        columns.extend([cookies.c.cookie_name, line_items.c.quantity, line_items.c.extended_cost])
        joins = joins.join(line_items).join(cookies)
    cust_orders = select(columns)
    cust_orders = cust_orders.select_from(joins).where(users.c.username == cust_name)
    if shipped:
        cust_orders = cust_orders.where(orders.c.shipped == shipped)
    result = conn.execute(cust_orders).fetchall()
    return result


# Gets all orders.
print(get_orders_by_customer('cakeeater'))

# Gets all orders with details.
print(get_orders_by_customer('cakeeater', details=True))

# Gets only orders that have shipped.
# print(get_orders_by_customer('cakeeater', shipped=True))

# Gets orders that haven’t shipped yet with details.
print(get_orders_by_customer('cakeeater', shipped=False, details=True))

"""
    Exceptions and Transactions
"""
from sqlalchemy.exc import IntegrityError

"""
    :AttributeError
    We will start with an AttributeError that occurs when you attempt to access an attribute that doesn’t exist.
    This often occurs when you are attempting to access a column on a ResultProxy that isn’t present.
    AttributeErrors occur when you try to access an attribute of an object that isn’t present on that object.
    You’ve probably run into this in normal Python code.
    I’m singling it out because this is a common error in SQLAlchemy and it’s very easy to miss the reason why it is occuring.
    To demonstrate this error, let’s insert a record into our users table and run a query against it. Then we’ll try
    to access a column on that table that we didn’t select in the query”

"""

query = select([users])
results = conn.execute(query).fetchall()

try:
    print(results[0].address)
except AttributeError as error:
    print("AttributeError !!")
    # print(error.orig.message, error.params)

"""
    :IntegrityError
    Another common SQLAlchemy error is the IntegrityError, which occurs when we try to do something that would violate
    the constraints configured on a Column or Table. This type of error is commonly encountered in cases
    where you require something to be unique—for example, if you attempt to create two users with the same username,
    an IntegrityError will be thrown because usernames in our users table must be unique.

"""

ins = insert(users).values(
    username="cookiemon",
    email_address="damon@cookie.com",
    phone="111-111-1111",
    password="password"
)

try:
    result = conn.execute(ins)
except IntegrityError as error:
    print("Integrity Error !!")
    # print(error.orig.message, error.params)

# NOTE
# Remember it is best practice to wrap as little code as possible in a try/except block and only catch specific errors.
# This prevents catching unexpected errors that really should have a different behavior
# than the catch for the specific error you’re watching for.

