# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
##  SMTP Mail plugin
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import smtplib
import socket
import subprocess
import shlex
from email.mime.text import MIMEText
from email.header import Header
import email.utils
## NOC modules
from noc.main.notify import Notify as NotifyBase
from noc.lib.validators import is_email


class Notify(NotifyBase):
    name = "mail"

    def send_message(self, params, subject, body, link=None):
        use_sendmail = bool(self.config.get(self.name, "command").strip())
        # Check params
        if not is_email(params):
            self.error("Invalid email: %s" % params)
            return True
        # Prepare message
        if link:
            body += "\n\nSee details: %s\n" % link
        from_address = self.config.get(self.name, "from_address")
        message = MIMEText(body, _charset="utf-8")
        message["From"] = from_address
        message["To"] = params
        message["Date"] = email.utils.formatdate()
        message["Subject"] = Header(subject, "utf-8")
        msg = message.as_string()
        self.debug(msg)
        if use_sendmail:
            # Spool via sendmail
            cmd = self.config.get(self.name, "command",
                "/usr/sbin/sendmail -t -i")
            c = shlex.split(cmd)
            self.debug("Spooling to %s" % c[0])
            try:
                p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
            except OSError, why:
                self.error("Failed to run %s: %s" % (c[0], why))
                return False
            p.stdin.write(msg)
            p.stdin.close()
        else:
            # Spool via SMTP
            # Connect to SMTP server
            smtp = smtplib.SMTP()
            self.debug("Connecting %s" % self.config.get(self.name,
                "smtp_server"))
            try:
                smtp.connect(self.config.get(self.name, "smtp_server"),
                    self.config.getint(self.name, "smtp_port"))
            except socket.error, why:
                self.error("SMTP error: %s" % str(why))
                return False
            smtp.ehlo(self.config.get(self.name, "helo_hostname"))
            # Enforce TLS when required
            if self.config.getboolean(self.name, "use_tls"):
                smtp.starttls()
                smtp.ehlo(self.config.get(self.name, "helo_hostname"))
            # Authenticate when necessary
            smtp_user = self.config.get(self.name, "smtp_user")
            smtp_password = self.config.get(self.name, "smtp_password")
            if smtp_user and smtp_password:
                self.debug("Authenticating as %s" % smtp_user)
                try:
                    smtp.login(smtp_user, smtp_password)
                except smtplib.SMTPAuthenticationError, why:
                    self.error("SMTP Authentication error: %s" % str(why))
                    return False
                # Send mail
            try:
                smtp.sendmail(from_address, [params], msg)
            except smtplib.SMTPSenderRefused, why:
                self.error("Sender refused: %s" % str(why))
                return False
            except smtplib.SMTPServerDisconnected, why:
                self.error("Server disconnected: %s" % str(why))
                return False
            except smtplib.SMTPDataError, why:
                self.error("Data error: %s" % str(why))
                return False
        return True
