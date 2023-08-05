# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Event Collector Interface
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
## Pythom modules
import logging
import time


class EventCollector(object):
    name = "EventCollector"
    INVALID_EVENT_SOURCE_DELAY = 60

    def __init__(self, activator):
        self.activator = activator
        self.invalid_sources = set()
        self.invalid_sources_flush = 0

    def debug(self, msg):
        logging.debug("[%s] %s" % (self.name, msg))

    def info(self, msg):
        logging.info("[%s] %s" % (self.name, msg))

    def error(self, msg):
        logging.error("[%s] %s" % (self.name, msg))

    def check_source_address(self, ip):
        t = int(time.time())
        r = True
        # Append to invalid sources if not passed the check
        if not self.activator.check_event_source(ip):
            self.invalid_sources.add(ip)
            r = False

        # Flush all pending invalid event sources when INVALID_EVENT_SOURCE_DELAY interval is expired
        if (self.invalid_sources and
            t - self.invalid_sources_flush >= self.INVALID_EVENT_SOURCE_DELAY):
            self.error("Invalid event sources in last %d seconds: %s" % (
                self.INVALID_EVENT_SOURCE_DELAY,
                ", ".join(self.invalid_sources)))
            for s in self.invalid_sources:
                # Generate "Invalid event source" Event
                self.process_event(t, "", {
                    "source"   : "system",
                    "component": "noc-activator",
                    "activator": self.activator.activator_name,
                    "collector": self.collector_signature,
                    "type"     : "Invalid Event Source",
                    "ip"       : s
                    })
            self.invalid_sources = set()
            self.invalid_sources_flush = t
        return r

    def process_event(self, timestamp, ip, body={}):
        self.activator.on_event(timestamp, ip, body)
