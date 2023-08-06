#!/usr/local/bin/python
#! -*- coding: utf-8 -*-


'''
'''

import os
import logging
from logging.handlers import SysLogHandler

#todo: needs a test if syslog is actually up...

def get_logger(modname, confd):
    '''simple, pre-configured logger will be returned.
       
    if envvar: use_logging == False will return NullHandler logger.
    '''


    if confd['use_logging'] == 'Y':
        lg = logging.getLogger(modname)
        lg.setLevel(confd['loglevel'])
        ch = SysLogHandler(confd['syslog_sock'])
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        lg.addHandler(ch)
    else:
        lg = logging.getLogger(modname)
        lg.addHandler(logging.NullHandler())        

    return lg



def simple_logger(modname, confd):
    """
    Factory class.  
    Depending on inputs return a no-op logger 
     or configured logger.
    
    logging process:
      write out to stdout - we should assume we log everything and let parsers sort it out      later.  See 12factor app for expansion of idea.

    
    Hmmm, abandon after ten mins thought.  Nice idea but just use std logger perhaps
    """   
  
    format = """[log][%s][%%s][%%s]%%s""" % modname
    dtformat = "%Y%M%D-%H:%m:%s"
    #factory???
    if confd['use_logging'] == 'Y':
        def rhaptos2_stdout_logger(msg, level="info"):
            dt = datetime.datetime.today().strftime(dtformat)
            print format % (dt, level, msg) 
        return rhaptos2_stdout_logger
    else:
        def rhaptos2_noop_logger(msg):
            pass
        return rhaptos2_noop_logger


