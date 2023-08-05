### -*- coding: utf-8 -*- #############################################
# Разработано компанией Стерх (http://sterch.net/)
# Все права защищены, 2010
#
# Developed by Sterch (http://sterch.net/)
# All right reserved, 2010
#######################################################################

""" Workers for sterch.conveyor package """

__author__  = "Polshcha Maxim (maxp@sterch.net)"
__license__ = "ZPL"

import sys
import traceback
import types

from assistance import InQueueMixin, OutQueueMixin, EventMixin, LogMixin
from interfaces import IFirstWorker, ILastWorker, IRegularWorker
from Queue import Empty, Full
from threading import Thread
from time import sleep
from zope.component import getUtility
from zope.interface import implements

class FirstWorker(EventMixin, 
                  OutQueueMixin, 
                  LogMixin,
                  Thread):
    """ Initial worker """
    implements(IFirstWorker)
    
    def __init__(self, out_queue, event, delay, activity=None): 
        """    out_queue --- either object that provides IQueue or IQueue utility name
               event     --- either object that provides IEvent or IEvent utility name 
               delay     --- delay between activity cycles
               activity --- callable represents worker activity
        """
        Thread.__init__(self)
        self._out_queue = out_queue
        self.delay = delay
        self._event = event
        if activity:
            self.activity = activity
                
    def activity(self):
        raise NotImplementedError("Must be defined")
    
    def run(self):
        """ Worker's workcycle """
        while True:
            if self.event.isSet(): return
            try:
                for task in self.activity():
                    while True:
                        try:
                            self.out_queue.put(task, timeout=self.delay)
                            break
                        except Full, ex:
                            pass
            except Exception, ex:
                # Thread must stop if and only if event is set
                self.traceback(ex)

class LastWorker(EventMixin, 
                 InQueueMixin,
                 LogMixin,
                 Thread):
    """ Last worker """
    implements(ILastWorker)
    
    def __init__(self, in_queue, event, delay, activity=None): 
        """    in_queue --- either object that provides IQueue or IQueue utility name
               event     --- either object that provides IEvent or IEvent utility name 
               delay     --- delay between activity cycles
               activity --- callable represents worker activity
        """
        Thread.__init__(self)
        self._in_queue = in_queue
        self.delay = delay
        self._event = event
        if activity:  self.activity = activity
    
    def activity(self):
        raise NotImplementedError("Must be defined")
    
    def run(self):
        """ Worker's workcycle """
        while True:
            if self.event.isSet(): return
            try:
                try:
                    task = self.in_queue.get(timeout=self.delay)
                    self.activity(task)                        
                except Empty, ex:
                    pass
            except Exception, ex:
                # Thread must stop if and only if event is set
                self.traceback(ex)


class Worker(EventMixin, 
             InQueueMixin,
             OutQueueMixin,
             LogMixin,
             Thread):
    """ Regular worker to process elements from input queue to output queue.
        Could be stopped be setting event. 
    """
    implements(IRegularWorker)
    
    def __init__(self, in_queue, out_queue, event, delay, activity=None):
        """ 
            in_queue --- input queue
            out_queue --- output queue
            timeout --- time to wait in inqueue is empty and check evtAllDone
            event --- event to stop thread activity
            activity --- callable represents worker activity. Must accept only one argument --- item.
                        Returned value will be placed to out_queue if not None.
        """
        Thread.__init__(self)
        self._in_queue = in_queue
        self._out_queue = out_queue
        self.delay = delay
        self._event = event
        self.activity = activity
        if activity: self.activity = activity
        
    def activity(self, item):
        raise NotImplementedError("Must be implemented")
    
    def run(self):
        """ Worker cycle """
        while True:
            if self.event.isSet(): return
            try:
                try:
                    task = self.in_queue.get(timeout=self.delay)
                    for new_task in self.activity(task):
                        while True:
                            try:
                                self.out_queue.put(new_task, timeout=self.delay)
                                break
                            except Full, ex:
                                pass
                except Empty, ex:
                    pass
            except Exception, ex:
                # Thread must stop if and only if event is set
                self.traceback(ex)
                
RegularWorker = Worker