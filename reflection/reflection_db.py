from sqlalchemy import MetaData, create_engine, Table

metadata = MetaData()
engine = create_engine('sqlite:///Chinook_Sqlite.sqlite')

"""
    :Reflection
    Reflection is a technique that allows us to populate a SQLAlchemy object from an existing database.
    You can reflect tables, views, indexes, and foreign keys.

    + however, instead of defining the columns by hand, we are going to use the autoload and
    autoload_with keyword arguments.

    + This will reflect the schema information into the metadata object and store
    a reference to the table in the artist variable.”

"""

artist = Table('artist', metadata, autoload=True, autoload_with=engine)
album = Table('album', metadata, autoload=True, autoload_with=engine)

print(artist.columns.keys())
print(album.columns.keys())

"""
    Interestingly, the foreign key to the Artist table does not appear to have been reflected.
    Let’s check the foreign_keys attribute of the Album table to make sure that it is not present:
"""

print(album.foreign_keys)

"""
    So it really didn’t get reflected. This occurred because the two tables weren’t reflected at the same time,
    and the target of the foreign key was not present during the reflection.

    In an effort to not leave you in a semi-broken state, SQLAlchemy discarded the one-sided relationship.
    -> add the missing ForeignKey, and restore the relationship:”

"""

from sqlalchemy import ForeignKeyConstraint

album.append_constraint(
    ForeignKeyConstraint(['ArtistId'], ['artist.ArtistId'])
)

# check the schema of `album` table
print(metadata.tables)
print(metadata.tables['album'])

print(album.foreign_keys)

from sqlalchemy import select

s = select([artist]).limit(10)
results = engine.execute(s).fetchall()

for r in results:
    print(r)

"""
    Now let’s see if we can use the relationship to join the tables properly.
    We can run the following code to test the relationship:
"""

print(str(album.join(artist)))

"""
    Excellent!
    Now we can perform queries that use this relationship. It works just like the queries discussed in “Joins”.

"""

"""
    :Reflecting a Whole Database
    In order to reflect a whole database, we can use the reflect method on the metadata object.
    The reflect method will scan everything available on the engine supplied, and reflect everything it can.
    Let’s use our existing metadata and engine objects to reflect the entire Chinook database:
"""

# Reflecting a Whole Database
metadata.reflect(bind=engine)

print(metadata.tables.keys())
print(metadata.tables)

"""

    The tables we manually reflected are listed twice but with different case letters.
    This is due to that fact that SQLAlchemy reflects the tables as they are named,
    and in the Chinook database they are uppercase. Due to SQLite’s handling of case sensitivity,
    both the lower- and uppercase names point to the same tables in the database.

"""

playlist = metadata.tables['Album']

from sqlalchemy import select
s = select([playlist]).limit(10)
li = engine.execute(s).fetchall()
print(li)

"""
    :NB:
    Reflection is a very useful tool; however, as of version 1.0 of SQLAlchemy,
    we cannot reflect CheckConstraints, comments, or triggers.
    You also can’t reflect client-side defaults or an association between a sequence and a column. However,
    it is possible to add them manually USING CHECKCONSTRAINTS, ForeignKeys

    :Example
    check print(album.foreign_keys)
    from sqlalchemy import ForeignKeyConstraint

    album.append_constraint(
    ForeignKeyConstraint(['ArtistId'], ['artist.ArtistId']))

    check now after adding the join between `album` and `artist` print(album.foreign_keys)
"""
