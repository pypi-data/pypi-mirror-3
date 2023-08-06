"""Define CMFNotification specific exceptions.

$Id: exceptions.py 112940 2010-03-14 01:15:51Z WouterVH $
"""


class MailHostNotFound(Exception):
    """Could not send notification: no mailhost found"""


class DisabledFeature(Exception):
    """Cannot use this feature: it is disabled"""


class InvalidEmailAddress(Exception):
    """The given email address is not valid"""
