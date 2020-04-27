# sqlalchemy-orm

#### + Database Design :

![database-design](./figures/database_design.png)

#### + install sqlalchemy :
    - without c-extensions:
        --+ During the install, SQLAlchemy will attempt to build some C extensions,
            which are leveraged to make working with result sets fast and more memory efficient.
            If you need to disable these extensions due to the lack of a compiler on the system
            you are installing on, you can use --global-option=--without-cextensions.

            Note that using SQLAlchemy without C extensions will adversely affect performance,
            and you should test your code on a system with the C extensions prior to optimizing it.

            pip install --global-option=--without-cextensions sqlalchemy

Best practices &amp; Patterns to use SQLAlchemy-CORE &amp; SQLAlchemy ORM, for big applications

###  + ORM       |  Python     | SQLIte
![typing](./figures/typing-(ORM_Python_SQLite).png)


### + ClauseElements - select

![ClauseElements](./figures/ClauseElements.png)


### + Successful transaction flow

![transaction-workflow](./figures/transaction_workflow.png)

### + transaction Error

![transaction-workflow](./figures/transaction_error.png)

    + However, if one or more of those statements fail, we can catch that error and use the prior state to roll back back any statements that succeeded.
     Figure above shows a transaction workflow in error.”

#### -> run tests:
    cd SQLAlchemy_BASICS_OPS
    python -m unittest test_app

#### -> create db sqlite from script sql:
    - from sql to db
       + cat chinook_db.sql | sqlite3 chnook.db
       + sqlite3 chnook.db < chinook_db.sql

    - from db to sql
        + sqlite3 Chinook_Sqlite.sqlite .dump > chinook_db.sql

#### -> Generate Code for a Class From a database:
    - pip install sqlacodegen
    - sqlacodegen sqlite:///Chinook_Sqlite.sqlite > models.py
    # models.py file where you want to write the result.
    # sqlite:///Chinook_Sqlite.sqlite make sure that the database exist in the directory where you run the command.
    - sqlacodegen sqlite:///Chinook_Sqlite.sqlite --tables Artist,Track
    # you can choice tables that you want to generate

#### -> Migration - Alembic
    - Setup Environment for database migration
        + alembic init migration
        + cd migration
        + alembic init alembic
        + add in Alembic/envy.py:
            sys.path.append(os.getcwd()) -> (helps python to find modules)

            from app.db import Base
            target_metadata = Base.metadata -> change target metadata

    - Building Migration
        + Create Empty Migration
          alembic revision -m "Empty Init"
          alembic upgrade head
          alembic revision --autogenerate -m "Added Cookie model"
          alembic current
          alembic downgrade 34044511331
          alembic upgrade 34044511331:2e6a6cc63e9 --sql # migrating from 34044511331 to 2e6a6cc63e9 and show sql
          alembic upgrade 34044511331:2e6a6cc63e9 --sql > migration.sql

    - WARNING :
        If you develop on one database backend (such as SQLite) and deploy to a different database (such as PostgreSQL),
        make sure to change the sqlalchemy.url configuration setting that we set to use the connection string for a PostgreSQL database.
        If not, you could get SQL output that is not correct for your production database! To avoid issues such as this,
        I always develop on the database I use in production.”


Excerpt From: Jason Myers and Rick Copeland. “Essential SQLAlchemy.” iBooks.
+ check [chinook_db](http://chinookdatabase.codeplex.com/) the database that we used in the reflection part.
