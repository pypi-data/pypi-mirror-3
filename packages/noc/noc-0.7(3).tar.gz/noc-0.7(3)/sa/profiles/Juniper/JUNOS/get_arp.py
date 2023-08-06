# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Juniper.JUNOS.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetARP

class Script(NOCScript):
    name = "Juniper.JUNOS.get_arp"
    implements = [IGetARP]

    rx_line = re.compile(
        r"^(?P<mac>[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2})\s+(?P<ip>\d+\.\d+\.\d+\.\d+)\s+(?P<interface>\S+)")

    def execute(self, vrf=None):
        if vrf:
            cmd = "show arp no-resolve vpn %s" % vrf
        else:
            cmd = "show arp no-resolve"
        return self.cli(cmd, list_re=self.rx_line)
