#!/usr/local/bin/python                                                                    

'''                                                                                        
Generic routines etc


>>> d
{'tinymce_store': '/tmp/tinymce'}
>>> 
pbrian@hadrian:common$ export tinymce_store=foo && python
Python 2.7.2 (default, Feb 14 2012, 00:43:33) 
[GCC 4.2.1 20070831 patched [FreeBSD]] on freebsd9
Type "help", "copyright", "credits" or "license" for more information.
>>> import conf
>>> d = conf.get_config('rhaptos2')
No file at /etc/rhaptos2.ini found. Could not find or could not process: /etc/rhaptos2.ini - No section: 'rhaptos2'
>>> d
{'tinymce_store': 'foo'}
>>> 

NB -0 we cannot inisialise logging before conf is finished so loggin conf stuff awkward   


if the appname is "bamboo"
either the config file is at

  /etc/bamboo.ini
  /usr/local/etc/bamboo.ini
  
or

  env var CONFIGFILE location

or 

  if any of the above have a variable in them, and that variable is also in 
  envvars, envvars overwrites the one in configfile

or

  if any envvar, in file or not, begins with appname_ it is brought in

    bamboo_myval


  
'''



import os
import ConfigParser
#from rhaptos2.common.exceptions import Rhaptos2Error
from err import Rhaptos2Error


def catch_log(msg):
    print "[log]" + msg
    

'''

useage

from rhaptos2.common import conf
confd = conf.get_config('appname')

'''

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


