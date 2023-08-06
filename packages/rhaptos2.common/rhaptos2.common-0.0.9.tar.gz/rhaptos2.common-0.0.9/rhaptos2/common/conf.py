#!/usr/local/bin/python                                                                    

'''                                                                                       
from rhaptos2.common import conf
confd = conf.get_config('appname')

tl;dr

  
  conf.get_config("foo") will do the following:
  
  create a dict to store all this in and populate it from:

  read /etc/foo.ini
  read /usr/local/foo.ini
  read .ini file at location os.environ("CONFIGFILE")
  overwrite any of the variable names in the above files with values 
   from *case sensitive matching* variable names in os.environ
  append any variable named foo_<xxx> in os.environ

   


 
    We simply expect there to be a file <appname>.ini at these locations:
   
    /etc/<appname>.ini
    /usr/local/etc/<appname>.ini

    (deprecating:and at whatever location CONFIGFILE= is in os.environ)
    OR
    We pick up the data from os.environ
    - 
    
    
    We expect to receive ConfigParser compiliant files at these
    locations 
    We expect there to be one section only, called appname

    We will turn these into one dict, and return it
 
    If we have *any* keys in os.environ that match those keys already
    specified in a file os.environ will overwrite the file values.  So
    don't call your key PATH


>>> os.environ['test_myvar'] = "Hello World"
>>> confd = get_config('test')
>>> confd
{'test_myvar': 'Hello World'}

'''



import os
import ConfigParser

from err import Rhaptos2Error


def get_config(appname):
    ''' 

    We simply expect there to be a file <appname>.ini at these locations:
   
    /etc/<appname>.ini
    /usr/local/etc/<appname>.ini

    (deprecating:and at whatever location CONFIGFILE= is in os.environ)
    OR
    We pick up the data from os.environ
    - 

    
    
    We expect to receive ConfigParser compiliant files at these
    locations 
    We expect there to be one section only, called appname

    We will turn these into one dict, and return it
 
    If we have *any* keys in os.environ that match those keys already
    specified in a file os.environ will overwrite the file values.  So
    don't call your key PATH


    '''

    confd = {}
    #todo: error check
    inifile = appname + ".ini"
    for loc in ('/etc', '/usr/local/etc'):
        confpath = os.path.join(loc, inifile)
        try:
            d = read_ini(confpath, appname)
            #brtue update - todo: log this stage carefully
            confd.update(d)    
        except Rhaptos2Error, e:
            pass
    

    if 'CONFIGFILE' in os.environ.keys(): 
        try:   
            d =  read_ini(os.environ['CONFIGFILE'], appname)
            confd.update(d)
        except Rhaptos2Error, e:
            pass

 
    ### overwrite from environment 
    for k in os.environ:
        if k in confd.keys():
            confd[k] = os.environ[k]
#            catch_log("overwriting %s -> %s (%s)" % (k, k, os.environ[k]))

    ### snaffle namespave from env
    ### If we find a rhaptos2_myvar: in the env, grab that too.
    for k in os.environ:
        if k.find(appname + "_") == 0:
            confd[k] = os.environ[k]
#            catch_log("overwriting %s -> %s (%s)" % (k, k, os.environ[k]))

    return confd    

def read_ini(filepath, appname):

    parser = ConfigParser.SafeConfigParser()
    parser.optionxform = str     #case sensitive
    try:
        parser.read(filepath)
        d = dict(parser.items(appname))
    except Exception, e:
        raise Rhaptos2Error('Could not find or could not process: %s - %s' % (filepath, e) )

    return d
    

def version():
    pass
    #open(os.path.join(os.path.dirname(rhaptos2.common.conf.__file__), 'version.txt')).read().strip()
    #need to work out how to get __file__ back...



if __name__ == '__main__':
    import doctest
    doctest.testmod()
