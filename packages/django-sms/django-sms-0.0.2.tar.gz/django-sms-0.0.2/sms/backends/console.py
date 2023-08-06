import sys

from sms.backends.base import BaseSMSBackend

class SMSBackend(BaseSMSBackend):
    """
    Write SMS to console

    """
    def __init__(self):
        self.stream = sys.stdout

    def send_sms(self, text, from_, to):
        self.stream.write(to)
        self.stream.write(from_,)
        self.stream.write(text)
        self.stream.flush()
