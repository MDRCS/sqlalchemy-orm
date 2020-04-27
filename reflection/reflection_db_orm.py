from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

Base = automap_base()

from sqlalchemy import create_engine

engine = create_engine('sqlite:///Chinook_Sqlite.sqlite')

Base.prepare(engine, reflect=True)

"""
    :Reflecting a Database with Automap
    In order to reflect a database, instead of using the declarative_base we’ve been using with the ORM so far,
    we’re going to use the automap_base.
"""

print(Base.classes.keys())

Artist = Base.classes.Artist
Album = Base.classes.Album

from sqlalchemy.orm import Session

session = Session(engine)
for artist in session.query(Artist).limit(10):
    print(artist.ArtistId, artist.Name)

# Reflected Relationships

artist = session.query(Artist).first()
for album in artist.album_collection:
    print('{} - {}'.format(artist.Name, album.Title))


