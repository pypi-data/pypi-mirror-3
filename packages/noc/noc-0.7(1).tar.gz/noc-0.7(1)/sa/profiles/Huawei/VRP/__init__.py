# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Huawei
## OS:     VRP
## Compatible: 3.1
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET,SSH
import re

class Profile(noc.sa.profiles.Profile):
    name="Huawei.VRP"
    supported_schemes=[TELNET,SSH]
    pattern_more="^  ---- More ----"
    pattern_prompt=r"^[<#]\S+?[>#]"
    command_more=" "
    config_volatile=["^%.*?$"]
    command_disable_pager="screen-length 0 temporary"

    def generate_prefix_list(self,name,pl,strict=True):
        p="ip ip-prefix %s permit %%s"%name
        if not strict:
            p+=" le 32"
        return "undo ip ip-prefix %s\n"%name+"\n".join([p%x.replace("/"," ") for x in pl])

    rx_interface_name=re.compile(r"^(?P<type>[A-Z]+E)(?P<number>[\d/]+)$")
    def convert_interface_name(self,s):
        """
        >>> Profile().convert_interface_name("GE2/0/0")
        'GigabitEthernet2/0/0'
        """
        match=self.rx_interface_name.match(s)
        if not match:
            return s
        return "%s%s"%({"GE": "GigabitEthernet"}[match.group("type")],match.group("number"))

    def convert_mac(self, mac):
        """
        Convert 00:11:22:33:44:55 style MAC-address to 0011-2233-4455
        """
        v = mac.replace(":", "").lower()
        return "%s-%s-%s" % (v[:4], v[4:8], v[8:])
