'''
envvar
======

Provides:
    Reads a file containing <var>=<value> and loads in a container, 
    so you can use container.var
    
    getVarFromFile(filename,container)
    
Use:
    
::
db = getVarFromFile('config/db.cfg','db')
::
    
Notes: 
    In order to work the "container" parameter must be the name of the container <var>.
    In the example db is the <var> and container='db'
Reference:
    http://stackoverflow.com/questions/924700/
         best-way-to-retrieve-variable-values-from-a-text-file-python-json
'''


def getVarFromFile(filename,name):
    import imp
    f = open(filename)
    glbvar = imp.load_source(name, '', f)
    f.close()
    return glbvar

if __name__ == "__main__":
    test = getVarFromFile('test/file.cfg','test')
    print test.VAR2
    
