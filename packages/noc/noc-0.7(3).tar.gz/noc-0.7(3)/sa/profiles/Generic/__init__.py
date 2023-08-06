# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Generic.Host
## Dummb profile to allow managed object creating
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET, SSH


class Profile(noc.sa.profiles.Profile):
    name = "Generic.Host"
    supported_schemes = [TELNET, SSH]
