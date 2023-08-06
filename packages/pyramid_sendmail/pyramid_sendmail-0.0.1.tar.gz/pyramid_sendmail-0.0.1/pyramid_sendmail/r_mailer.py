from email.message import Message
from email.generator import Generator

from zope.interface import implements
from repoze.sendmail.interfaces import IMailer

import os

from repoze.sendmail.delivery import copy_message


class SendmailMailer(object):
    implements(IMailer)

    sendmail_app = '/usr/sbin/sendmail'
    sendmail_template = "%(sendmail_app)s -t -i -f %(sender)s"

    # sendmail vars
    ## -f sender | Set the envelope sender address.  This is where delivery problems are sent to
    ## -frsender | Set the envelope sender address.  This is where delivery problems are sent to
    ## -i        | When  reading  a message from standard input, don't treat a line with only a . character as the end of input.
    ## -oi       | When  reading  a message from standard input, don't treat a line with only a . character as the end of input.
    ## -t        | Extract recipients from message headers. These are added to  any recipients specified on the command line.


    def __init__(self, sendmail_app=None , sendmail_template=None ):
        if sendmail_app :
            self.sendmail_app = sendmail_app
        if sendmail_template :
            self.sendmail_template = sendmail_template

    def send(self, fromaddr, toaddrs, message):
        if isinstance(message, Message):
            message = message.as_string()

        p= os.popen( self.sendmail_template % { 'sendmail_app':self.sendmail_app , 'sender' : fromaddr }, "w")
        p.write(message)
        status = p.close()
        if status :
            raise RuntimeError("Could not excecute sendmail properly")
