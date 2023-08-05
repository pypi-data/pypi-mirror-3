# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## EdgeCore.ES.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetChassisID
##
## EdgeCore.ES.get_chassis_id
##
class Script(NOCScript):
    name="EdgeCore.ES.get_chassis_id"
    cache=True
    implements=[IGetChassisID]
    
    ##
    ## ES4626
    ##
    rx_mac_4626=re.compile(r"\d+\s+(?P<id>\S+).*?System\s+CPU",re.IGNORECASE|re.MULTILINE)
    @NOCScript.match(platform__contains="4626")
    def execute_4626(self):
        v=self.cli("show mac-address-table static")
        match=self.re_search(self.rx_mac_4626, v)
        return match.group("id")
    
    ##
    ## Other
    ##
    rx_mac=re.compile(r"MAC Address[^:]*?:\s*(?P<id>\S+)",re.IGNORECASE|re.MULTILINE)
    @NOCScript.match()
    def execute_other(self):
        v=self.cli("show system")
        match=self.re_search(self.rx_mac, v)
        return match.group("id")
    
