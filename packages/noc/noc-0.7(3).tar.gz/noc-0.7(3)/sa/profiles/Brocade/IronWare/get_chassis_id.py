# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Brocade.IronWare.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetChassisID


class Script(NOCScript):
    """
    Brocade.IronWare.get_chassis_id
    """
    name = "Brocade.IronWare.get_chassis_id"
    implements = [IGetChassisID]
    rx_mac = re.compile(r"([0-9a-f]{4}.[0-9a-f]{4}.[0-9a-f]{4})",
                        re.IGNORECASE | re.MULTILINE | re.DOTALL)

    def execute(self):
        v = self.cli("show chassis")
        match = self.re_search(self.rx_mac, v)
        return match.group(1)
