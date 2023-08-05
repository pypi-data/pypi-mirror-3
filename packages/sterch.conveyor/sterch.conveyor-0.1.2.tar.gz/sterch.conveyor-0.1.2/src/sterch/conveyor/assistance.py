### -*- coding: utf-8 -*- #############################################
# Разработано компанией Стерх (http://sterch.net/)
# Все права защищены, 2010
#
# Developed by Sterch (http://sterch.net/)
# All right reserved, 2010
#######################################################################

""" Help classes

"""
__author__  = "Polshcha Maxim (maxp@sterch.net)"
__license__ = "ZPL"

import traceback
import sys

from sterch.queue.interfaces import IQueue
from sterch.logfile.interfaces import ILog
from sterch.threading.interfaces import IEvent
from StringIO import StringIO
from zope.cachedescriptors.property import CachedProperty
from zope.component import getUtility, queryUtility

class OutQueueMixin(object):
    @CachedProperty
    def out_queue(self):
        if IQueue(self._out_queue, None): 
            return self._out_queue
        return getUtility(IQueue, name=self._out_queue)

class InQueueMixin(object):
    
    def has_tasks(self):
        """ Does queue have unfinished tasks. """
        return not self.in_queue.empty()
    
    def tasks_count(self):
        """ Return number of unfinished tasks. """
        return self.in_queue.qsize()

    @CachedProperty
    def in_queue(self):
        if IQueue(self._in_queue, None): 
            return self._in_queue
        return getUtility(IQueue, name=self._in_queue)

class EventMixin(object):
    @CachedProperty
    def event(self):
        if IEvent(self._event, None): 
            return self._event
        return getUtility(IEvent, name=self._event)
    
class LogMixin(object):
    @CachedProperty
    def log(self):
        log = queryUtility(ILog)
        class Log(object):
            def message(self, value): print value
        log = Log() if not log else log
        return log
    
    def traceback(self, ex):
        msg = "ERROR:" + str(ex)
        tb = StringIO()
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        traceback.print_exception(exceptionType, exceptionValue, exceptionTraceback, file=tb)
        msg = msg + "\n" + tb.getvalue()
        if self.log: 
            self.log.message(msg)
        else:
            print msg