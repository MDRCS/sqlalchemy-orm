from sqlalchemy import create_engine

# Relative Path for Unix Systems
# SQLite & In-Memory db
engine1 = create_engine('sqlite:///cookies.db')
engine2 = create_engine('sqlite:///:memory:')

# Postgresdb
#engine3 = create_engine('postgresql+psycopg2://username:password@localhost:5432/mydb')

# MySQL db - Remote db Server (pool_recycle for cycles to check the connection with the database)
#engine4 = create_engine('mysql+pymysql://cookiemonster:chocolatechip'
#                        '@mysql01.monster.internal/cookies', pool_recycle=3600)

# Open the connection
conn = engine1.connect()

"""
    Some optional keywords for the create_engine function are:

    `echo`
    This will log the actions processed by the engine, such as SQL statements and their parameters.
    It defaults to false.

    `encoding`
    This defines the string encoding used by SQLAlchemy. It defaults to utf-8, and mostDBAPIs support this encoding by default.
    This does not define the encoding type used by the backend database itself.

    `isolation_level`
    This instructs SQLAlchemy to use a specific isolation level.
    For example, PostgreSQL with Psycopg2 has READ COMMITTED, READ UNCOMMITTED, REPEATABLE READ, SERIALIZABLE,
    and AUTOCOMMIT available with a default of READ COMMITTED.
    PyMySQL has the same options with a default of REPEATABLE READ for InnoDB databases.”

    `pool_recycle`
    This recycles or times out the database connections at regular intervals. This is important for MySQL due to
    the connection timeouts we mentioned earlier. It defaults to -1, which means there is no timeout.”

"""


"""
    In Example 1-1:
    - we create a table that could be used to store the cookie inventory
      for our online cookie delivery service.
"""

from sqlalchemy import MetaData

metadata = MetaData()

from sqlalchemy import Table, Column, Integer, String, Numeric, DateTime

cookies = Table('cookies', metadata,
                Column('cookie_id', Integer(), primary_key=True),
                Column('cookie_name', String(55), index=True),
                Column('cookie_recipe_url', String(255)),
                Column('cookie_sku', String(55)),
                Column('quantity', Integer()),
                Column('unit_cost', Numeric(12, 2)))

"""

1- Notice the way we marked this column as the table’s primary key. More on this in a second.

2- We’re making an index of cookie names to speed up queries on this column.

3- This is a column which takes multiple arguments, length and precision,
   such as 11.2, which would give us numbers up to 11 digits long with two decimal places.

"""

"""
    “Example 1-2. Another Table with more Column options
    - Table for user model

"""

from datetime import datetime

users = Table('users', metadata,
              Column('user_id', Integer(),primary_key=True),
              Column('username', String(15), nullable=False, unique=True),
              Column('email_address', String(255), nullable=False),
              Column('phone', String(20), nullable=False),
              Column('password', String(25), nullable=False),
              Column('created_on', DateTime(), default=datetime.now),
              Column('updated_on', DateTime(), default=datetime.now, onupdate=datetime.now)
              )
"""

1- Here we are making this column required (nullable=False) and also requiring a unique value.
2- The default sets this column to the current time if a date isn’t specified.
3- Using onupdate here will reset this column to the current time every time any part of the record is updated.

"""


"""
    CAUTION
    You’ll notice that we set default and onupdate to the callable datetime.now instead of the function call itself,
    datetime.now(). If we had used the function call itself, it would have set the default to the time when the table was first instantiated.
    By using the callable, we get the time that each individual record is instantiated and updated.”

    -> so the best practice is to use the callable datetime.now instead of calling the function directly
"""
