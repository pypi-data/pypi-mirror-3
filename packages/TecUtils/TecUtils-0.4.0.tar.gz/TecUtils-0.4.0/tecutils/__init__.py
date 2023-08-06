'''
========
tecutils
========

tecutils provides various utilities to accelerate development
of programs design to use MySQL as a database and substitute
the use of global variables.

tecutils contains the following modules:

- mydb
- envvar
- simplecrypt

mydb
====

Requires:
    mysql-python (sudo apt-get install python-mysqldb)
    
Provides:
    There are three functions that take care the database interaction:
    
    - GetRecordset(sHost,sUser,sPwd,sDB,sSQL)
    - GetData(sHost,sUser,sPwd,sDB,sSQL)
    - ExecuteSQL(sHost,sUser,sPwd,sDB,sSQL)::
    
    from tecutils.mydb import ExecuteSQL, GetData, GetRecordset

    myHost = "localhost"
    myUser = "root"
    myPwd = "password"
    myDB = "test"

    ExecuteSQL(myHost, myUser, myPwd, myDB, "INSERT INTO animal (name, category) VALUES " + \
      ('snake', 'reptile'), ('frog', 'amphibian'), ('tuna', 'fish'), ('racoon', 'mammal'), 
      ('lizard', 'reptile')")
    
    sql="SELECT name FROM animal WHERE category='reptile'"
    GetRecordset(myHost, myUser, myPwd, myDB,sql)

    thistype='fish'
    sql="SELECT name FROM animal WHERE category='%s'" % thistype
    GetData(myHost, myUser, myPwd, myDB,sql)


envvar
======

Provides:
    Reads a file containing <var>=<value> and loads in a container, so you can use container.var
    
    getVarFromFile(filename,container)
    
Use::

    from tecutils import getVarFromFile
    db = getVarFromFile('config/db.cfg','db')



Examples
--------

If use the two modules provides a way to use a configuration file to access de database::


    # this is the config file:
    # db.cfg
    HOST = 'localhost'
    USER = 'root'
    PWD = 'password'
    DB = 'test'


and use it in a program::

    from tecutils.envvar import getVarFromFile
    from tecutils.mydb import GetRecordset

    getVarFromFile('db.cfg',db)

    data = GetRecordset(db.HOST,db.USER,db.PWD,db.DB,"SELECT * FROM animal")
    for animal in data:
        print animal[0]


simplecrypt
===========

Many thanks to the Dabo team: Ed Leafe and Paul McNett (http://dabodev.com)
for this simple utility to "obscure" passwords so casual browsing on the database
connection info doesn't show the real one.

Use::

    from tecutils.simplecrypt import simplecrypt
    pwd = 'foobar'
    crypt = SimpleCrypt()
    pwd = crypt.encrypt(pwd)
  
  
or using the example from envvars::

    crypt = SimpleCrypt()
    db.PWD = crypt.decrypt(db.PWD)
'''