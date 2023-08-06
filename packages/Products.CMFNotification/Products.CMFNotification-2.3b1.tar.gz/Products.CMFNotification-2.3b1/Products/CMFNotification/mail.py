import logging
from ZODB.POSException import ConflictError
from zope.interface import implements
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import MessageFactory
from Products.CMFNotification.utils import encodeMailHeaders
from Products.CMFNotification import NotificationTool
from Products.CMFNotification.exceptions import MailHostNotFound
from Products.CMFNotification.interfaces import INotificationDelivery

LOG = logging.getLogger('CMFNotification.mail')

_ = MessageFactory('cmfnotification')

class MailNotificationDelivery(object):
    implements(INotificationDelivery)

    @property
    def description(self):
        return _(u'mail_notification_delivery_description',
                   default=u'Notify by email')

    def notify(self, obj, user, what, label, bindings):
        mtool = getToolByName(obj, 'portal_membership')
        member = mtool.getMemberById(str(user))
        if member is None:
            return 0
        email = member.getProperty('email', '')
        if not email:
            return 0
        if not NotificationTool.EMAIL_REGEXP.match(email):
            return 0

        pn = getToolByName(obj, 'portal_notification')
        template = pn.getTemplate(obj, what, bindings)
        if template is None:
            LOG.warning("No mail template for label '%s' for "\
                        "'%s' notification of '%s'",
                        label, what, obj.absolute_url(1))
            return 0

        try:
            message = template(**bindings)
        except ConflictError:
            raise
        except:
            LOG.error("Cannot evaluate mail template '%s' on '%s' "\
                      "for '%s' for label '%s'",
                      template.absolute_url(1),
                      obj.absolute_url(1), what, label,
                      exc_info=True)
            return 0
        return self.sendNotification(obj, email, message)

    def sendNotification(self, obj, address, message):
        """Send ``message`` to ``address``."""
        portal = obj.restrictedTraverse('@@plone_portal_state').portal()
        mailhosts = portal.superValues(NotificationTool.MAIL_HOST_META_TYPES)
        if not mailhosts:
            raise MailHostNotFound
        mailhost = mailhosts[0]

        ptool = getToolByName(obj, 'portal_properties').site_properties
        encoding = ptool.getProperty('default_charset', 'utf-8')
        message = encodeMailHeaders(message, encoding)

        this_message = ('To: %s\n' % address) + message
        this_message = this_message.encode(encoding)
        try:
            mailhost.send(this_message)
        except ConflictError:
            raise
        except:
            LOG.error('Error while sending '\
                      'notification: \n%s' % this_message,
                      exc_info=True)
            return 0
        return 1
