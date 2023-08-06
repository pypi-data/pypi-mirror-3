from sms.backends.base import BaseSMSBackend
import sms

class SMSBackend(BaseSMSBackend):
    """
    A SMS backend for use during test sessions.
    Stores all outgoing SMS's in sms.outbox rather than sending them.

    """
    def __init__(self, *args, **kwargs):
        super(SMSBackend, self).__init__(*args, **kwargs)
        if not hasattr(sms, 'outbox'):
            sms.outbox = []

    def send_sms(self, text, from_, to):
        sms.outbox.append({'text': text, 'from': from_, 'to': to})
