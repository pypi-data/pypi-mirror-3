# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Extreme.XOS.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetConfig

class Script(noc.sa.script.Script):
    name="Extreme.XOS.get_config"
    implements=[IGetConfig]
    def execute(self):
        config=self.cli("show config")
        return self.cleaned_config(config)
