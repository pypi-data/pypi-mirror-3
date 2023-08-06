from pyramid_mailer import Mailer as pyramid_mailer_Mailer

from email.message import Message
from email.generator import Generator

from zope.interface import implements
from repoze.sendmail.interfaces import IMailer

from .r_mailer import SendmailMailer
from .r_delivery import SendmailDelivery


class Mailer(pyramid_mailer_Mailer):

    def __init__(self,**kwargs):
        """ we're going to wrap the pyramid_mailer.mailer.Mailer class , but figure out some sendmail functionality first """

        sendmail_app = None
        sendmail_template = None
        if 'sendmail_app' in kwargs:
            sendmail_app = kwargs['sendmail_app']
        if 'sendmail_template' in kwargs:
            sendmail_template = kwargs['sendmail_template']
        if sendmail_app :
            self.sendmail_mailer = SendmailMailer( sendmail_app , sendmail_template )
        else:
            self.sendmail_mailer = SendmailMailer()
        self.sendmail_delivery = SendmailDelivery(self.sendmail_mailer)

        ## ok, let the superclass take over
        pyramid_mailer_Mailer.__init__( self , **kwargs )


    def send_sendmail(self, message ):
        """
        Sends a message within the transaction manager.

        Uses the local sendmail option

        :param message: a **Message** instance.
        """
        return self.sendmail_delivery.send(*self._message_args(message))


    def send_immediately_sendmail(self, message, fail_silently=False):
        """
        Sends a message immediately, outside the transaction manager.

        Uses the local sendmail option

        If there is a connection error to the mail server this will have to
        be handled manually. However if you pass ``fail_silently`` the error
        will be swallowed.

        :param message: a **Message** instance.

        :param fail_silently: silently handle connection errors.
        """

        try:
            return self.sendmail_mailer.send(*self._message_args(message))
        except :
            if not fail_silently:
                raise
