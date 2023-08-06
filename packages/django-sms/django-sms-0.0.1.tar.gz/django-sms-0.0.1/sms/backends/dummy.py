from sms.backends.base import BaseSMSBackend

class SMSBackend(BaseSMSBackend):
    """
    Dummy SMS backend that does nothing.

    """

    def send_sms(self, text, from_, to):
        pass
