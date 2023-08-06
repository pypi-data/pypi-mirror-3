from repoze.sendmail.delivery import AbstractMailDelivery
from repoze.sendmail.delivery import MailDataManager

from zope.interface import implements
from repoze.sendmail.interfaces import IMailDelivery


class SendmailDelivery(AbstractMailDelivery):
    implements(IMailDelivery)

    def __init__(self, mailer):
        self.mailer = mailer

    def createDataManager(self, fromaddr, toaddrs, message):
        return MailDataManager(self.mailer.send,
                               args=(fromaddr, toaddrs, message))
