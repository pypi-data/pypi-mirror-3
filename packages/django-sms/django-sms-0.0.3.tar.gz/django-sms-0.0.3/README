===============
django-sms
===============

A Django app for sending SMS with interchangable backends.

Requirements
============

Required
--------

* Python 2.5+
* Django 1.2+

Backends
========

* 'sms.backends.dummy.SMSBackend'
* 'sms.backends.locmem.SMSBackend'
* 'sms.backends.console.SMSBackend'

Writing a custom backend
========================

You can write your own SMS backend by subclassing BaseSMSBackend and overriding the send_sms method.

::

    class SMSBackend(BaseSMSBackend):
        """
        My custom sms backend

        """
        def __init__(self):
            self.client = MyClient(settings.KEY, settings.SECRET)

        def send_sms(self, message, from_, to):
            self.client.send_message(message, from_, to)

Usage
=====

    (1) Add an SMS backend to SMS_BACKEND in settings.py.

    ::

        SMS_BACKEND = 'sms.backends.console.SMSBackend'

    (2) call send_sms

    ::

        from sms import send_sms

        send_sms(text, from_, to)

Testing
=======

::

    sms.original_sms_backend = settings.SMS_BACKEND
    settings.SMS_BACKEND = 'sms.backends.locmem.SMSBackend'
    sms.outbox = []

    sms.send_sms('my message', 'me', 'you')
    self.assertIn('message', sms.outbox[0]['text'])
