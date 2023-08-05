# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Brocade.IronWare.add_vlan
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IAddVlan


class Script(NOCScript):
    """
    Brocade.IronWare.add_vlan
    """
    name = "Brocade.IronWare.add_vlan"
    implements = [IAddVlan]

    def execute(self, vlan_id, name, tagged_ports):
        with self.configure():
            self.cli("vlan %d name %s" % (vlan_id, name))
            if tagged_ports:
                self.cli("tagged " + " ".join(tagged_ports))
            self.cli("exit")
        self.save_config()
        return True
