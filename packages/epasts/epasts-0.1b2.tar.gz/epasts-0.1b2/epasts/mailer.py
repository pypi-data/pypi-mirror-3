##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

# Minor modifications.

import socket
from smtplib import SMTP
from email.message import Message
from subprocess import Popen, PIPE

from epasts.message import Message as EpastsMessage

class Mailer(object):

    def send(self, message):
        """Send epasts.message.Message
        """

        assert isinstance(message, EpastsMessage)

        fromaddr = message.sender
        toaddrs = message.send_to
        msg = message.to_message()
        return self.send_pure(fromaddr, toaddrs, msg)

    def send_pure(self, fromaddr, toaddrs, message):
        """Send python email.message.Message or str.
        """
        raise NotImplementedError()

class SmtpMailer(Mailer):
    smtp = SMTP

    def __init__(self, hostname='localhost', port=25,
                 username=None, password=None, no_tls=False, force_tls=False, debug_smtp=False):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.force_tls = force_tls
        self.no_tls = no_tls
        self.debug_smtp = debug_smtp

    def smtp_factory(self):
        connection = self.smtp(self.hostname, str(self.port))
        connection.set_debuglevel(self.debug_smtp)
        return connection

    def send_pure(self, fromaddr, toaddrs, message):
        """Send python email.message.Message or str.
        """

        if isinstance(message, Message):
            message = message.as_string()

        connection = self.smtp_factory()

        # send EHLO
        code, response = connection.ehlo()
        if code < 200 or code >= 300:
            code, response = connection.helo()
            if code < 200 or code >= 300:
                raise RuntimeError('Error sending HELO to the SMTP server '
                                   '(code=%s, response=%s)' % (code, response))

        # encryption support
        have_tls =  connection.has_extn('starttls')
        if not have_tls and self.force_tls:
            raise RuntimeError('TLS is not available but TLS is required')

        have_ssl = hasattr(socket, 'ssl')
        if have_tls and have_ssl and not self.no_tls:
            connection.starttls()
            connection.ehlo()

        if connection.does_esmtp:
            if self.username is not None and self.password is not None:
                connection.login(self.username, self.password)
        elif self.username:
            raise RuntimeError('Mailhost does not support ESMTP but a username '
                                'is configured')

        connection.sendmail(fromaddr, toaddrs, message)
        try:
            connection.quit()
        except socket.sslerror:
            #something weird happened while quiting
            connection.close()

class SendmailMailer(Mailer):

    def send_pure(self, fromaddr, toaddrs, message):
        """Send python email.message.Message or str.
        """

        if isinstance(message, Message):
            message = message.as_string()

        toaddrs = list(toaddrs)

        args = ["sendmail"]
        args.extend(toaddrs)
        p = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)

        out, err = p.communicate(input=message)

        if p.returncode != 0:
            raise Exception(out, err)
