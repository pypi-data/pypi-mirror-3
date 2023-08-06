'''
mydb
====

Requires:
    mysql-python
    
Provides:
    There are three functions that take care the database interaction:
    
    - GetRecordset(sHost,sUser,sPwd,sDB,sSQL)
    - GetData(sHost,sUser,sPwd,sDB,sSQL)
    - ExecuteSQL(sHost,sUser,sPwd,sDB,sSQL)
    
::
import TecUtils.mydb

myHost = "localhost"
myUser = "root"
myPwd = "password"
myDB = "test"


TecUtils.mydb.ExecuteSQL(myHost, myUser, myPwd, myDB, "INSERT INTO animal (name, category) VALUES " + \
    ('snake', 'reptile'), ('frog', 'amphibian'), ('tuna', 'fish'), ('racoon', 'mammal'), ('lizard', 'reptile')")
    
sql="SELECT name FROM animal WHERE category='reptile'"
TecUtils.mydb.GetRecordset(myHost, myUser, myPwd, myDB,sql)

thistype='fish'
sql="SELECT name FROM animal WHERE category='%s'" % thistype
TecUtils.mydb.GetData(myHost, myUser, myPwd, myDB,sql)
::

'''

import sys
import MySQLdb


def GetRecordset(sHost,sUser,sPwd,sDB,sSQL):
    '''Returns a list of lists of data.'''

    try:
        conn = MySQLdb.connect (host = sHost,
                                user = sUser,
                                passwd = sPwd,
                                db = sDB)
    except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])
        sys.exit (1)

    try:
        cursor = conn.cursor ()
        cursor.execute (sSQL)
        result_set = cursor.fetchall ()
        cursor.close ()
        return result_set
        
    except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])
        sys.exit (1)

    cursor.close ()
    conn.commit ()
    conn.close ()

    
def GetData(sHost,sUser,sPwd,sDB,sSQL):
    '''Returns a list of data.'''

    try:
        conn = MySQLdb.connect (host = sHost,
                                user = sUser,
                                passwd = sPwd,
                                db = sDB)
    except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])
        sys.exit (1)

    try:
        cursor = conn.cursor ()
        cursor.execute (sSQL)
        result_set = cursor.fetchone ()
        cursor.close ()
        return result_set
        
    except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])
        sys.exit (1)

    cursor.close ()
    conn.commit ()
    conn.close ()

    
def ExecuteSQL(sHost,sUser,sPwd,sDB,sSQL):
    '''Execute de sSQL command, nothing is return.'''

    try:
        conn = MySQLdb.connect (host = sHost,
                                user = sUser,
                                passwd = sPwd,
                                db = sDB)
    except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])
        sys.exit (1)

    try:
        cursor = conn.cursor ()
        cursor.execute (sSQL)
        cursor.close ()
        
    except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])
        sys.exit (1)

    cursor.close ()
    conn.commit ()
    conn.close ()

    
if __name__ == "__main__":
    myHost = "localhost"
    myUser = "root"
    myPwd = "ahivoy"
    myDB = "test"


    ExecuteSQL(myHost, myUser, myPwd, myDB, "INSERT INTO animal (name, category) VALUES ('snake', 'reptile'), ('frog', 'amphibian'), ('tuna', 'fish'), ('racoon', 'mammal')")
  