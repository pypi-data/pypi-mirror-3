# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Linksys.SPS2xx.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetVersion
import re

rx_sys=re.compile(r"System Description:\s+(?P<platform>.+?$)\s*$", re.MULTILINE|re.DOTALL)
rx_ver=re.compile(r"SW version\s+(?P<version>\S+)", re.MULTILINE|re.DOTALL)

class Script(noc.sa.script.Script):
    name="Linksys.SPS2xx.get_version"
    cache=True
    implements=[IGetVersion]
    def execute(self):
        v=self.cli("show system")
        match_sys=rx_sys.search(v)
        v=self.cli("show version")
        match_ver=rx_ver.search(v)
        return {
            "vendor"    : "Linksys",
            "platform"  : match_sys.group("platform"),
            "version"   : match_ver.group("version"),
        }
