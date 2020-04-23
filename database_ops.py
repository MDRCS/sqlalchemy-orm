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
