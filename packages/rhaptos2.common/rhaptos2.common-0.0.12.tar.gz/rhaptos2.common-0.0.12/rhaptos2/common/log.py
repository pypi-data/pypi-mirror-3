#!/usr/local/bin/python
#! -*- coding: utf-8 -*-


'''

'''

import os
import logging
from logging.handlers import SysLogHandler
from logging import StreamHandler
import pprint
import statsd


class StatsdHandler(logging.Handler):
    """Logging Handler class that emits statsd calls to graphite, then stdout
    
    It *only* does incr logs, ie event counting.
    Thats probably appropriate for most all log related stats

    We want to log to  

    c = statsd.StatsClient(app.config['rhaptos2_statsd_host'],
           int(app.config['rhaptos2_statsd_port']))


    issues - we init with host and port, probably a bad idea.
    Just do not want to muck around with config mdule for logging yet.

    >>> lg = logging.getLogger("doctest") 
    >>> h = StatsdHandler("localhost", 2222)
    >>> lg.addHandler(h)
    >>> lg.warn("test")

    """
    def __init__(self, host, port):
        logging.Handler.__init__(self)
        self.stats_client = statsd.StatsClient(
                                               host,
                                               port)

    def emit(self, record):
        if "statsd" not in record.__dict__.keys():
            pass # hmmm no logging in the logger?
        else:
            for s in record.statsd:
                self.stats_client.incr(s)
        


# lg = logging.getLogger("test")
# hdlr = StatsdLog('www','1100')
# hdlr2 = logging.StreamHandler()

# formatter = logging.Formatter('%(asctime)s - \
# %(name)s - %(levelname)s  - %(message)s')
# hdlr.setFormatter(formatter)
# hdlr2.setFormatter(formatter)

# lg.addHandler(hdlr)
# lg.addHandler(hdlr2)


# lg.warn("Help", extra={'statsd':['rhaptos2.repo.module', 
#                                    'bamboo.foo.bar']})





def get_logger(modname, confd):
    '''simple, pre-configured logger will be returned.
       
    >>> l = get_logger("test", {'test_use_logging':'Y', 
    ...                         'test_loglevel':"DEBUG"})
    >>> l.info("Whoops")


    if envvar: use_logging == False will return NullHandler logger.
    '''
    #Trapping basic missing conf
    uselogging = "%s_use_logging" % modname
    loglevel = "%s_loglevel" % modname

    if uselogging not in confd.keys():
        confd[uselogging] = 'Y'

    if loglevel not in confd.keys():
        confd[loglevel] = 'DEBUG'


    if confd['%s_use_logging' % modname] == 'Y':
        lg = logging.getLogger(modname)
        lg.setLevel(confd['%s_loglevel' % modname])
        ch = StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        lg.addHandler(ch)
    else:
        lg = logging.getLogger(modname)
        lg.addHandler(logging.NullHandler())        

    return lg



def simple_logger(modname, confd):
    """

    Not currently used. 
    Factory class.  
    Depending on inputs return a no-op logger 
     or configured logger.
    
    logging process: write out to stdout - we should assume we log
      everything and let parsers sort it out later.  See 12factor app
      for expansion of idea.

    
    Hmmm, abandon after ten mins thought.  Nice idea but just use std logger perhaps
    """   
  
    format = """[log][%s][%%s][%%s]%%s""" % modname
    dtformat = "%Y%M%D-%H:%m:%s"
    #factory???
    if confd['%s_use_logging' % modname] == 'Y':
        def rhaptos2_stdout_logger(msg, level="info"):
            dt = datetime.datetime.today().strftime(dtformat)
            print format % (dt, level, msg) 
        return rhaptos2_stdout_logger
    else:
        def rhaptos2_noop_logger(msg):
            pass
        return rhaptos2_noop_logger


if __name__ == '__main__':
    import doctest
    doctest.testmod()
