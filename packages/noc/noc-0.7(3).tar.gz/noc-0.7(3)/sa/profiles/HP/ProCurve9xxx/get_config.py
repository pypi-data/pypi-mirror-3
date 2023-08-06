# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.ProCurve9xxx.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetConfig


class Script(NOCScript):
    name = "HP.ProCurve9xxx.get_config"
    implements = [IGetConfig]

    def execute(self):
        config = self.cli("show config")
        config = self.strip_first_lines(config, 2)
        return self.cleaned_config(config)
