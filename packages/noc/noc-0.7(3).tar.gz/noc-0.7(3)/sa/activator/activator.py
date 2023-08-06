# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Service Activator Daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
from __future__ import with_statement
import os
import logging
import time
import re
import sys
import Queue
import cPickle
from threading import Lock
## NOC modules
from noc.sa.profiles import profile_registry
from noc.sa.script import script_registry
from noc.sa.script.ssh.keys import Key
from noc.sa.rpc import file_hash, get_digest,\
                       PROTOCOL_NAME, PROTOCOL_VERSION, PUBLIC_KEYS,\
                       CIPHERS, MACS, COMPRESSIONS, KEY_EXCHANGES
from noc.sa.protocols.sae_pb2 import *
from noc.sa.activator.servers import ServersHub
from noc.lib.fileutils import safe_rewrite, read_file
from noc.lib.daemon import Daemon
from noc.lib.fsm import FSM, check_state
from noc.lib.nbsocket import SocketFactory
from noc.lib.debug import DEBUG_CTX_CRASH_PREFIX
from noc.sa.activator.service import Service
from noc.sa.activator.activator_socket import ActivatorSocket
from noc.sa.activator.fping_socket import FPingProbeSocket
from noc.sa.activator.pm_collector_socket import PMCollectorSocket


class Activator(Daemon, FSM):
    """
    Activator daemon
    """
    daemon_name = "noc-activator"
    FSM_NAME = "Activator"
    DEFAULT_STATE = "IDLE"
    STATES = {
        ## Starting stage. Activator is idle, all servers are down
        "IDLE": {
                "timeout" : "CONNECT",
                "close"   : "IDLE",
                },
        ## Beginning TCP connection
        "CONNECT" : {
                "timeout" : "IDLE",
                "refused" : "IDLE",
                "close"   : "IDLE",
                "connect" : "CONNECTED",
                },
        ## TCP connection established
        "CONNECTED" : {
                "timeout" : "IDLE",
                "close"   : "IDLE",
                "setup"   : "SETUP",
                "upgrade" : "UPGRADE",
                "error"   : "IDLE",
        },
        ## Protocol version negotiated
        ## Crypto algorithms setup
        "SETUP" : {
                "timeout" : "IDLE",
                "close"   : "IDLE",
                "error"   : "IDLE",
                "kex"     : "KEX",
                "plaintext" : "REGISTER"
        },
        ## Key exchange
        "KEX": {
                "timeout" : "IDLE",
                "close"   : "IDLE",
                "error"   : "IDLE",
                "register": "REGISTER"
        },
        ## Start registration
        "REGISTER": {
            "timeout" : "IDLE",
            "close"   : "IDLE",
            "error"   : "IDLE",
            "registred" : "REGISTRED"
        },
            
        "REGISTRED" : {
                "timeout" : "IDLE",
                "auth"    : "AUTHENTICATED",
                "close"   : "IDLE",
                "error"   : "IDLE",
        },
        "AUTHENTICATED" : {
                "caps"    : "CAPS",
                "close"   : "IDLE",
        },
        "UPGRADE" : {
                "setup"   : "SETUP",
                "close"   : "IDLE",
                "refused" : "IDLE"
        },
        "CAPS" : {
                "establish" : "ESTABLISHED",
        },
        "ESTABLISHED" : {
                "close"   : "IDLE",
        }
    }

    def __init__(self):
        Daemon.__init__(self)
        self.activator_name = self.config.get("activator", "name")
        logging.info("Running activator '%s'" % self.activator_name)
        # Check wrether activator started in bundle or in stand-alone mode
        self.stand_alone_mode = (self.config.get("activator", "software_update")
                                 and not os.path.exists(os.path.join("sa", "sae", "sae.py")))
        self.service = Service()
        self.service.activator = self
        self.factory = SocketFactory(tick_callback=self.tick, controller=self)
        self.children = {}
        self.sae_stream = None
        self.to_listen = False  # To start or not to start collectors
        self.object_mappings = {}  # source -> object_id
        self.ignore_event_rules = []  # [(left_re,right_re)]
        self.trap_collectors = []  # List of SNMP Trap collectors
        self.syslog_collectors = []  # List of SYSLOG collectors
        self.pm_data_collectors = []  # List of PM Data collectors
        self.to_save_output = False  # Do not save canned result
        self.use_canned_session = False  # Do not use canned session
        logging.info("Loading profile classes")
        profile_registry.register_all()  # Should be performed from ESTABLISHED state
        script_registry.register_all()
        self.nonce = None
        FSM.__init__(self)
        self.next_mappings_update = None
        self.next_crashinfo_check = None
        self.next_heartbeat = None
        self.script_threads = {}
        self.max_script_threads = self.config.getint("activator", "max_scripts")
        self.script_lock = Lock()
        self.script_call_queue = Queue.Queue()
        self.pm_data_queue = []
        self.pm_result_queue = []
        self.pm_data_secret = self.config.get("activator", "pm_data_secret")
        self.servers = ServersHub(self)
        # CLI debug logging
        self.log_cli_sessions = self.config.getboolean("main",
                                                       "log_cli_sessions")
        self.log_cli_sessions_path = self.config.get("main",
                                                     "log_cli_sessions_path")
        self.log_cli_sessions_ip_re = re.compile(self.config.get("main",
                                                "log_cli_sessions_ip_re"))
        self.log_cli_sessions_script_re = re.compile(self.config.get("main",
                                                "log_cli_sessions_script_re"))
        # SSH keys
        self.ssh_public_key = None
        self.ssh_private_key = None
        self.load_ssh_keys()

    def load_ssh_keys(self):
        """
        Initialize ssh keys
        """
        private_path = self.config.get("ssh", "key")
        public_path = private_path + ".pub"
        # Load keys
        self.debug("Loading private ssh key from '%s'" % private_path)
        s_priv = read_file(private_path)
        self.debug("Loading public ssh key from '%s'" % public_path)
        s_pub = read_file(public_path)
        # Check all keys presend
        if s_priv is None or s_pub is None:
            self.error("Cannot find ssh keys. Generate one by './noc generate-ssh-keys' command")
            os._exit(1)
        self.ssh_public_key = Key.from_string(s_pub)
        self.ssh_private_key = Key.from_string_private_noc(s_priv)

    def error(self, msg):
        logging.error(msg)

    def on_IDLE_enter(self):
        """
        Entering IDLE state
        """
        if self.sae_stream:
            self.sae_stream.close()
            self.sae_stream = None
        if self.to_listen:
            if self.trap_collectors:
                self.stop_trap_collectors()
            if self.syslog_collectors:
                self.stop_syslog_collectors()
            if self.pm_data_collectors:
                self.stop_pm_data_collectors()
        self.set_timeout(3)

    def on_CONNECT_enter(self):
        """
        Entering CONNECT state
        """
        self.set_timeout(10)
        self.sae_stream = ActivatorSocket(self.factory,
                                          self.config.get("sae", "host"),
                                          self.config.getint("sae", "port"),
                self.config.get("sae", "local_address"))

    def on_CONNECTED_enter(self):
        """
        Entering CONNECTED state
        """
        self.set_timeout(10)
        if self.stand_alone_mode:
            self.event("upgrade")
        else:
            logging.info("Bundled packaging. Skipping software updates")
            self.protocol()

    def on_SETUP_enter(self):
        """
        Entering SETUP state
        """
        self.set_timeout(10)
        self.session_setup()

    def on_KEX_enter(self):
        """
        Entering key exchange state
        """
        self.set_timeout(10)
        self.kex()
    
    def on_REGISTER_enter(self):
        """
        Entering REGISTER state
        """
        self.set_timeout(10)
        self.register()
        
    def on_REGISTRED_enter(self):
        """
        Entering REGISTERED state
        """
        self.set_timeout(10)
        self.auth()

    def on_AUTHENTICATED_enter(self):
        """
        Entering AUTHENTICATED state
        """
        self.set_timeout(10)
        self.event("caps")

    def on_UPGRADE_enter(self):
        """
        Entering UPGRADE state
        """
        logging.info("Requesting software update")
        self.manifest()

    def on_CAPS_enter(self):
        """
        Entering CAPS state
        """
        logging.info("Sending capabilities")
        self.send_caps()

    def on_ESTABLISHED_enter(self):
        """
        Entering ESTABLISHED state
        """
        to_refresh_filters = False
        self.next_mappings_update = None
        # Check does our instance is designated to listen
        self.to_listen = self.config.get("activator", "listen_instance") == self.instance_id
        if self.to_listen:
            if self.config.get("activator", "listen_traps"):
                self.start_trap_collectors()
                to_refresh_filters = True
            if self.config.get("activator", "listen_syslog"):
                self.start_syslog_collectors()
                to_refresh_filters = True
            if self.config.get("activator", "listen_pm_data"):
                self.start_pm_data_collectors()
                to_refresh_filters = True
        if to_refresh_filters:
            self.get_object_mappings()
        if self.stand_alone_mode:
            self.check_crashinfo()

    def start_trap_collectors(self):
        """
        Start SNMP Trap Collectors
        """
        logging.debug("Starting trap collectors")
        from noc.sa.activator.trap_collector import TrapCollector
        self.trap_collectors = [
            TrapCollector(self, ip, port)
            for ip, port
            in self.resolve_addresses(self.config.get("activator", "listen_traps"), 162)
        ]

    def stop_trap_collectors(self):
        """
        Stop SNMP Trap Collectors
        """
        if self.trap_collectors:
            logging.debug("Stopping trap collectors")
            for tc in self.trap_collectors:
                tc.close()
            self.trap_collectors = []

    def start_syslog_collectors(self):
        """
        Start syslog collectors
        """
        logging.debug("Starting syslog collectors")
        from noc.sa.activator.syslog_collector import SyslogCollector
        self.syslog_collectors = [
            SyslogCollector(self, ip, port)
            for ip, port
            in self.resolve_addresses(self.config.get("activator", "listen_syslog"), 514)
        ]

    def stop_syslog_collectors(self):
        """
        Disable syslog collectors
        """
        if self.syslog_collectors:
            logging.debug("Stopping syslog collectors")
            for sc in self.syslog_collectors:
                sc.close()
            self.syslog_collectors = []

    def start_pm_data_collectors(self):
        """
        Launch PM Data collectors
        """
        logging.debug("Starting PM Data collectors")
        self.pm_data_collectors = [
            PMCollectorSocket(self, ip, port)
            for ip, port
            in self.resolve_addresses(self.config.get("activator", "listen_pm_data"), 19704)
        ]

    def stop_pm_data_collectors(self):
        """
        Disable PM Data collectors
        """
        if self.pm_data_collectors:
            logging.debug("Stopping PM Data collectors")
            for pdc in self.pm_data_collectors:
                pdc.close()
            self.pm_data_collectors = []

    def can_run_script(self):
        """
        Check max_scripts limit is not exceeded
        """
        with self.script_lock:
            return len(self.script_threads) < self.max_script_threads

    def run_script(self, script_name, access_profile, callback,
                   timeout, **kwargs):
        """
        Begin script execution
        """
        pv, pos, sn = script_name.split(".", 2)
        profile = profile_registry["%s.%s" % (pv, pos)]()
        script_class = script_registry[script_name]
        if not timeout:
            timeout = script_class.TIMEOUT
        script = script_class(profile, self, access_profile, timeout, **kwargs)
        logging.info("Script %s(%s). Timeout set to %s" % (script_name,
                                            access_profile.address, timeout))
        with self.script_lock:
            self.script_threads[script] = callback
            logging.info("%d script threads (%d max)" % (
                len(self.script_threads), self.max_script_threads))
        script.start()

    def on_script_exit(self, script):
        if script.e_timeout:
            s = "is timed out"
        elif script.e_cancel:
            s = "is cancelled"
        elif script.login_error:
            s = "cannot log in"
        else:
            s = "is completed"
        logging.info("Script %s(%s) %s" % (script.name,
                                           script.access_profile.address, s))
        with self.script_lock:
            cb = self.script_threads.pop(script)
            logging.info("%d script threads left (%d max)" % (
                len(self.script_threads), self.max_script_threads))
        cb(script)

    def request_call(self, f, *args, **kwargs):
        logging.debug("Requesting call: %s(*%s,**%s)" % (f, args, kwargs))
        self.script_call_queue.put((f, args, kwargs))

    def ping_check(self, addresses, callback):
        def cb(afi, afi_left, result, unreachable):
            result += unreachable
            afi_left.remove(afi)
            if not afi_left:
                callback(result)

        ipv4_addresses = [a for a in addresses if ":" not in a]
        ipv6_addresses = [a for a in addresses if ":" in a]

        fping = self.config.get("path", "fping")
        fping6 = self.config.get("path", "fping6")

        result = []
        afi_left = set()
        #
        if ipv4_addresses:
            afi_left.add("4")
        if fping6 and ipv6_addresses:
            afi_left.add("6")
        # Launch probes
        if ipv4_addresses:
            FPingProbeSocket(self.factory, fping, ipv4_addresses,
                             lambda x: cb("4", afi_left, result, x))
        if fping6 and ipv6_addresses:
            FPingProbeSocket(self.factory, fping6, ipv6_addresses,
                             lambda x: cb("6", afi_left, result, x))

    def map_event(self, source):
        """
        Map event source to object id
        :param source: Event source
        :type source: str
        :return: object id or None
        :rtype: str or None
        """
        return self.object_mappings.get(source)

    def run(self):
        """
        Main event loop
        """
        self.factory.run(run_forever=True)

    def tick(self):
        """
        Called every second
        """
        t = time.time()
        # Request filter updates
        if (self.get_state() == "ESTABLISHED" and self.next_mappings_update and
            t > self.next_mappings_update):
            self.get_object_mappings()
        # Check for pending crashinfos
        if (self.stand_alone_mode  and self.get_state() == "ESTABLISHED" and
            self.next_crashinfo_check and t > self.next_crashinfo_check):
            self.check_crashinfo()
        # Perform delayed calls
        while not self.script_call_queue.empty():
            try:
                f, args, kwargs = self.script_call_queue.get_nowait()
            except Queue.Empty:
                break
            logging.debug("Calling delayed %s(*%s,**%s)" % (f, args, kwargs))
            apply(f, args, kwargs)
        # Send collected PM data
        if self.get_state() == "ESTABLISHED" and self.pm_data_queue:
            self.send_pm_data()
        # Cancel stale scripts
        if self.get_state() == "ESTABLISHED":
            self.cancel_stale_scripts()
        # Heartbeat when necessary
        if (self.heartbeat_enable and
            (self.next_heartbeat is None or self.next_heartbeat <= t)):
            self.heartbeat()
            self.next_heartbeat = t + 3  # @todo: more accurate
        # Run default daemon/fsm machinery
        super(Activator, self).tick()

    def register_stream(self, stream):
        logging.debug("Registering stream %s" % str(stream))
        self.streams[stream] = None

    def release_stream(self, stream):
        logging.debug("Releasing stream %s" % str(stream))
        del self.streams[stream]

    def reboot(self):
        logging.info("Rebooting")
        os.execv(sys.executable, [sys.executable] + sys.argv)

    @check_state("CONNECTED", "UPGRADE")
    def protocol(self):
        """ Start protocol negotiation """
        def protocol_callback(transaction, response=None, error=None):
            if self.get_state() != "CONNECTED":
                return
            if error:
                logging.error("Protocol negotiation error: %s" % error.text)
                self.event("error")
                return
            if (response.protocol != PROTOCOL_NAME or
                response.version != PROTOCOL_VERSION):
                logging.error("Protocol negotiation failed")
                self.event("error")
                return
            logging.info("Protocol version negotiated")
            if self.stand_alone_mode:
                self.event("upgrade")
            else:
                logging.info("In-bundle package. Skiping software updates")
                self.event("setup")

        logging.info("Negotiation protocol '%s' version '%s'" % (
            PROTOCOL_NAME, PROTOCOL_VERSION))
        r = ProtocolRequest(protocol=PROTOCOL_NAME, version=PROTOCOL_VERSION)
        self.sae_stream.proxy.protocol(r, protocol_callback)
    
    @check_state("SETUP")
    def session_setup(self):
        """ Start crypto negotiations"""
        def setup_callback(transaction, response=None, error=None):
            if self.get_state() != "SETUP":
                return
            if error:
                logging.error("Crypto negotiation failed: %s" % e.text)
                self.event("error")
                return
            if response.key_exchange == "none":
                self.event("plaintext")
            else:
                self.sae_stream.set_next_transform(response.key_exchange,
                                                   response.public_key,
                                                   response.cipher,
                                                   response.mac,
                                                   response.compression)
                self.event("kex")

        r = SetupRequest(
            key_exchanges=KEY_EXCHANGES,
            public_keys=PUBLIC_KEYS,
            ciphers=CIPHERS,
            macs=MACS,
            compressions=COMPRESSIONS
        )
        self.sae_stream.proxy.setup(r, setup_callback)

    @check_state("KEX")
    def kex(self):
        """
        Perform key exchange
        """
        def kex_callback(transaction, response=None, error=None):
            if self.get_state() != "KEX":
                return
            if error:
                logging.error("Key exchange failed: %s" % error.text)
                self.event("error")
                return
            self.sae_stream.complete_kex(response)
            self.sae_stream.activate_next_transform()
            self.event("register")

        self.sae_stream.start_kex(kex_callback)

    @check_state("REGISTER")
    def register(self):
        def register_callback(transaction, response=None, error=None):
            if self.get_state() != "REGISTER":
                return
            if error:
                logging.error("Registration error: %s" % error.text)
                self.event("error")
                return
            logging.info("Registration accepted")
            self.nonce = response.nonce
            self.event("registred")
        logging.info("Registering as '%s'" % self.config.get("activator", "name"))
        r = RegisterRequest()
        r.name = self.activator_name
        self.sae_stream.proxy.register(r, register_callback)

    @check_state("REGISTRED")
    def auth(self):
        def auth_callback(transaction, response=None, error=None):
            if self.get_state() != "REGISTRED":
                return
            if error:
                logging.error("Authentication failed: %s" % error.text)
                self.event("error")
                return
            logging.info("Authenticated")
            self.event("auth")
        name = self.config.get("activator", "name")
        logging.info("Authenticating as %s" % name)
        r = AuthRequest(
            name=name,
            digest=get_digest(name,
                              self.config.get("activator", "secret"),
                              self.nonce))
        self.sae_stream.proxy.auth(r, auth_callback)

    @check_state("UPGRADE")
    def manifest(self):
        def manifest_callback(transaction, response=None, error=None):
            if self.get_state() != "UPGRADE":
                return
            if error:
                logging.error("Manifest error: %s" % error.text)
                self.manifest_transaction = None
                return
            if transaction.id == self.manifest_transaction.id:
                update_list = [cs.name for cs in response.files
                               if (not os.path.exists(cs.name) or
                                   cs.hash != file_hash(cs.name))]
                self.manifest_transaction = None
                if update_list:
                    self.software_upgrade(update_list)
                else:
                    self.protocol()
                    self.event("setup")
            else:
                logging.error("Transaction id mismatch")
                self.manifest_transaction = None

        logging.info("Requesting manifest")
        r = ManifestRequest()
        self.manifest_transaction = self.sae_stream.proxy.manifest(r, manifest_callback)

    @check_state("UPGRADE")
    def software_upgrade(self, update_list):
        def software_upgrade_callback(transaction, response=None, error=None):
            if error:
                logging.error("Upgrade error: %s" % error.text)
                self.software_upgrade_transaction = None
                return
            if transaction.id == self.software_upgrade_transaction.id:
                logging.info("Upgrading software")
                for u in response.codes:
                    logging.info("Upgrade: %s" % u.name)
                    safe_rewrite(u.name, u.code)
                self.software_upgrade_transaction = None
                self.reboot()
            else:
                logging.error("Transaction id mismatch")
                self.software_upgrade_transaction = None
        logging.debug("Requesting software upgrade for %s" % str(update_list))
        r = SoftwareUpgradeRequest()
        for f in update_list:
            r.names.append(f)
        self.software_upgrade_transaction = self.sae_stream.proxy.software_upgrade(r, software_upgrade_callback)

    @check_state("CAPS")
    def send_caps(self):
        def send_caps_callback(transaction, response=None, error=None):
            self.event("establish")

        r = SetCapsRequest()
        r.max_scripts = self.max_script_threads
        r.instance = str(self.instance_id)
        self.sae_stream.proxy.set_caps(r, send_caps_callback)

    @check_state("ESTABLISHED")
    def refresh_object_mappings(self):
        self.get_object_mappings()

    @check_state("ESTABLISHED")
    def get_object_mappings(self):
        def object_mappings_callback(transaction, response=None, error=None):
            if error:
                logging.error("get_object_mappings error: %s" % error.text)
                return
            self.object_mappings = dict((x.source, x.object)
                                        for x in response.mappings)
            self.compile_ignore_event_rules(response.ignore_rules)
            logging.debug("Setting object mappings to: %s" % self.object_mappings)
            self.next_mappings_update = time.time() + response.expire

        logging.info("Requesting object mappings")
        r = ObjectMappingsRequest()
        self.sae_stream.proxy.object_mappings(r, object_mappings_callback)

    @check_state("ESTABLISHED")
    def check_crashinfo(self):
        """
        When running in stand-alone mode, collect crashinfo files
        and send them as system events to SAE
        """
        if not self.config.get("main", "logfile"):
            return
        c_d = os.path.dirname(self.config.get("main", "logfile"))
        if not os.path.isdir(c_d):
            return
        for fn in [fn for fn in os.listdir(c_d) if fn.startswith(DEBUG_CTX_CRASH_PREFIX)]:
            # Load and unpickle crashinfo
            path = os.path.join(c_d, fn)
            with open(path) as f:
                data = cPickle.loads(f.read())  # @todo: Handle exception
            ts = data["ts"]
            del data["ts"]
            # Send event. "" is an virtual address of ROOT object
            self.on_event(ts, "", data)
            os.unlink(path)
        # Next check - after 60 seconds timeout
        self.next_crashinfo_check = time.time() + 60

    def on_event(self, timestamp, object, body):
        """
        Send FM event to SAE
        :param timestamp: Event timestamp
        :param object: Object id
        :param body: Event content
        """
        def on_event_callback(transaction, response=None, error=None):
            if error:
                logging.error("event_proxy failed: %s" % error)
        r = EventRequest()
        r.timestamp = timestamp
        r.object = object
        for k, v in body.items():
            # Check ignore rules
            for lr, rr in self.ignore_event_rules:
                if lr.search(k) and rr.search(v):
                    return  # Ignore event
            # Populate event request
            i = r.body.add()
            i.key = str(k)
            i.value = str(v)
        self.sae_stream.proxy.event(r, on_event_callback)

    def queue_pm_data(self, pm_data):
        self.pm_data_queue += pm_data

    def queue_pm_result(self, pm_result):
        self.pm_result_queue += pm_result

    def send_pm_data(self):
        """
        Send collected PM data to SAE
        """
        def pm_data_callback(transaction, response=None, error=None):
            if error:
                logging.error("pm_data failed: %s" % error)
        r = PMDataRequest()
        for probe_name, probe_type, timestamp, service, result, message in self.pm_result_queue:
            d = r.result.add()
            d.probe_name = probe_name
            d.probe_type = probe_type
            d.timestamp = timestamp
            d.service = service
            d.result = result
            d.message = message
        self.pm_result_queue = []
        for name, timestamp, is_null, value in self.pm_data_queue:
            d = r.data.add()
            d.name = name
            d.timestamp = timestamp
            d.is_null = is_null
            d.value = value
        self.pm_data_queue = []
        self.sae_stream.proxy.pm_data(r, pm_data_callback)

    def compile_ignore_event_rules(self, rules):
        self.ignore_event_rules = []
        for r in rules:
            try:
                logging.debug("Adding ignore rule: %s | %s" % (r.left_re,
                                                               r.right_re))
                self.ignore_event_rules += [(re.compile(r.left_re, re.IGNORECASE),
                                             re.compile(r.right_re, re.IGNORECASE))]
            except re.error, why:
                logging.error("Failed to compile ignore event rule: %s,%s. skipping" % (l, r))

    @check_state("ESTABLISHED")
    def cancel_stale_scripts(self):
        """
        Cancel stale scripts
        """
        to_cancel = [st for st in self.script_threads.keys() if st.is_stale() and not st.e_cancel]
        for script in to_cancel:
            logging.info("Cancelling stale script %s(%s)" % (
                script.name, script.access_profile.address))
            script.cancel_script()

    def SIGUSR1(self, signo, frame):
        """
        SIGUSR1 returns process info
        """
        s = [
            ["factory.sockets", len(self.factory)],
        ]
        if self.sae_stream:
            s += self.sae_stream.stats
        logging.info("STATS:")
        for n, v in s:
            logging.info("%s: %s" % (n, v))

    # SIGCHLD: Zombie hunting
    def SIGCHLD(self, signo, frame):
        """
        SIGCHLD begins zombie hunting
        """
        while True:
            try:
                pid, status = os.waitpid(-1, os.WNOHANG)
            except OSError:
                break
            if pid:
                logging.debug("Zombie pid=%d is hunted down and mercilessly killed" % pid)
            else:
                break
