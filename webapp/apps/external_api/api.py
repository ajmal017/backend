from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from importlib import import_module

"""
Inspired by http://charlesleifer.com/blog/django-patterns-pluggable-backends/
"""


def get_connection(path=None, fail_silently=False, **kwargs):
    """
    Load an sms backend and return an instance of it.
    :param string path: backend python path. Default: external_api.SmsBackend.MGageBackend
    :param bool fail_silently: Flag to not throw exceptions on error. Default: False
    :returns: backend class instance.
    :rtype: :py:class:`~sendsms.backends.base.BaseSmsBackend` subclass
    """

    path = path or getattr(settings, 'SMS_BACKEND', 'external_api.mgage.MGageBackend')
    try:
        mod_name, klass_name = path.rsplit('.', 1)
        mod = import_module(mod_name)
    except AttributeError as e:
        raise ImproperlyConfigured(u'Error importing sms backend module %s: "%s"' % (mod_name, e))

    try:
        klass = getattr(mod, klass_name)
    except AttributeError:
        raise ImproperlyConfigured('Module "%s" does not define a "%s" class' % (mod_name, klass_name))

    return klass(fail_silently=fail_silently, **kwargs)


def _connection(fail_silently=None, connection=None):
    """
    :param fail_silently: Flag to not throw exceptions on error.
    :param connection:
    :return:
    """
    connection = connection or get_connection(fail_silently=fail_silently)
    return connection


def send_sms(text, to, fail_silently=False,user=None, connection=None):
    """
    This uses the backend to send a single SMS.

    This should be used for a single message. For bulk messages, use
    `send_bulk_sms`
    """
    if not to:
        # We are not going to send a message to nobody so just fail
        return
    connection = _connection(fail_silently, connection)
    if isinstance(to, list):
        messages = []
        for i in to:
            messages.append({'body':text, 'to':i})
        return connection.send_messages(messages)
    elif isinstance(to, int):
        messages = [{'body':text, 'to':to}]
        return connection.send_messages(messages)

