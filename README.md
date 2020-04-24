# sqlalchemy-orm

#### + Database Design :

![database-design](./database_design.png)

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
![typing](./typing-(ORM_Python_SQLite).png)


### + ClauseElements - select

![ClauseElements](./ClauseElements.png)


### + Successful transaction flow

![transaction-workflow](./transaction_workflow.png)
