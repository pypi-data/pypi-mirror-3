========
tecutils
========

tecutils brinda varias utilerías para acelerar el desarrollo
de programas diseñados para usar MySQL como base de datos y 
substituye el uso de variables globales.

tecutils contiene los siguientes módulos:

- mydb
- envvar
- simplecrypt

mydb
====

Requiere:
    mysql-python (sudo apt-get install python-mysqldb)
    
Provee:
    Hay tres funciones que realizan la interacción con la base de datos:
    
    - GetRecordset(sHost,sUser,sPwd,sDB,sSQL)
    - GetData(sHost,sUser,sPwd,sDB,sSQL)
    - ExecuteSQL(sHost,sUser,sPwd,sDB,sSQL)::
    
    from tecutils.mydb import ExecuteSQL, GetData, GetRecordset
    myHost = "localhost"
    myUser = "root"
    myPwd = "password"
    myDB = "test"

    ExecuteSQL(myHost, myUser, myPwd, myDB, "INSERT INTO animal (name, category) VALUES " + \
      ('serpiente', 'reptil'), ('rana', 'amfibio'), ('atun', 'pez'), ('mapache', 'mamifero'), 
      ('lagartija', 'reptil')")
    
    sql="SELECT name FROM animal WHERE category='reptil'"
    datos = GetRecordset(myHost, myUser, myPwd, myDB,sql)
    print datos

    estetipo='pez'
    sql="SELECT name FROM animal WHERE category='%s'" % estetipo
    dato = GetData(myHost, myUser, myPwd, myDB,sql)
    print dato


envvar
======

Provee:
    Lee un archivo conteniendo <variable>=<valor> y carga un contenedor, 
    para que pueda usarse: contenedor.variable
    
    getVarFromFile(filename,container)
    
Uso::

    from tecutils import getVarFromFile
    db = getVarFromFile('config/db.cfg','db')



Ejemplos
--------

Si se usan los dos módulos se brinda una manera de usar archivos de 
configuración para accesar a la base de datos::

    # este es el archivo de configuracion:
    # db.cfg
    HOST = 'localhost'
    USER = 'root'
    PWD = 'hola'
    DB = 'pruebas'



y usarlo en el programa::

    from tecutils.envvar import getVarFromFile
    from tecutils.mydb import GetRecordset

    getVarFromFile('db.cfg',db)

    data = GetRecordset(db.HOST,db.USER,db.PWD,db.DB,"SELECT * FROM animal")
    for animal in data:
        print animal[0]


        
simplecrypt
===========

Muchas gracias al equipo de Dabo: Ed Leafe and Paul McNett (http://dabodev.com)
por esta sencilla utileria que "obscurece" las contraseñas para que la vista casual del
contenido de los archivos de conexión a la base de datos no muestren la información real.


Uso::

    from tecutils.simplecrypt import simplecrypt
    pwd = 'foobar'
    crypt = SimpleCrypt()
    pwd = crypt.encrypt(pwd)
  
  
o usando el ejemplo de envvars::

    crypt = SimpleCrypt()
    db.PWD = crypt.decrypt(db.PWD)
    

txt2pdf
=======

Convierte un archivo de texto en pdf.

Requiere reportlab y pyPDF para uso normal
para imprimir por windows se requiere el módulo win32api or que esté 
instalado ghostscript y ghostview

Uso: txt2pdf.py [optiociones] archivo_texto
El nombre del archivo de salida es el mismo que el de texto pero con extensión pdf.

Opciones:
  -h, --help            muestra este mensaje de ayuda y termina
  -c COPIES, --copies=COPIES
                        número de copias, solo válido con opcion -p
  -g                    imprimir a través de ghostprint, solo válido con opcion -w
  -m                    usar tamaño media carta como salida, omisión tamaño carta
  --output=OUTPUT       usar un nombre especifico de archivo de salida
  -p, --print           imprimir archivo despues de convertir
  --printer=PRINTER     impresora a enviar impresión, omisión: impresora predeterminada
  -w                    usar win32api para enviar archivo, solo válido con opcion -p
                        

