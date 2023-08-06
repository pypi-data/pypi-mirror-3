from .p_mailer import Mailer
from pyramid_mailer.interfaces import IMailer



def includeme(config):
    settings = config.registry.settings
    prefix = settings.get('pyramid_mailer.prefix', 'mail.')
    mailer = mailer_factory_from_settings(settings, prefix=prefix)
    config.registry.registerUtility(mailer, IMailer)

def mailer_factory_from_settings(settings, prefix='mail.'):
    return Mailer.from_settings(settings, prefix)

def get_mailer(request):
    registry = getattr(request, 'registry', None)
    if registry is None:
        registry = request
    return registry.getUtility(IMailer)
