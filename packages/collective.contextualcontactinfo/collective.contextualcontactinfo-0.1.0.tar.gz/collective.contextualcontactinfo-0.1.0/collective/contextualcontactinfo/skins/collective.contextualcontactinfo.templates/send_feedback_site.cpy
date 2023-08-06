## Controller Python Script "send_feedback_site"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Send feedback to portal administrator
##
REQUEST=context.REQUEST

from Products.CMFPlone.utils import transaction_note
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as pmf
from ZODB.POSException import ConflictError

##
## This may change depending on the called (portal_feedback or author)
state_success = "success"
state_failure = "failure"

plone_utils = getToolByName(context, 'plone_utils')
urltool = getToolByName(context, 'portal_url')
portal = urltool.getPortalObject()
url = urltool()

## make these arguments?
subject = REQUEST.get('subject', '')
message = REQUEST.get('message', '')
sender_from_address = REQUEST.get('sender_from_address', '')
sender_fullname = REQUEST.get('sender_fullname', '')
came_from = REQUEST.get('came_from', '')

send_to_address = portal.getProperty('email_from_address')
envelope_from = portal.getProperty('email_from_address')

state.set(status=state_success) ## until proven otherwise

host = context.MailHost # plone_utils.getMailHost() (is private)
encoding = portal.getProperty('email_charset')

variables = {'sender_from_address' : sender_from_address,
             'sender_fullname'     : sender_fullname,
             'url'                 : url,
             'subject'             : subject,
             'message'             : message,
             'came_from'		   : came_from
             }

try:
    message = context.site_feedback_template(context, **variables)
    try:
		result = host.send(message.encode(encoding), send_to_address, envelope_from,
                       	   subject=subject, charset=encoding)
    except:
		result = host.secureSend(message, send_to_address, envelope_from, subject=subject, subtype='plain', charset=encoding, debug=False, From=sender_from_address)
except ConflictError:
    raise
except: # TODO Too many things could possibly go wrong. So we catch all.
    exception = plone_utils.exceptionString()
    message = pmf(u'Unable to send mail: ${exception}',
                mapping={u'exception' : exception})
    plone_utils.addPortalMessage(message, 'error')
    return state.set(status=state_failure)

## clear request variables so form is cleared as well
REQUEST.set('message', None)
REQUEST.set('subject', None)
REQUEST.set('sender_from_address', None)
REQUEST.set('sender_fullname', None)
REQUEST.set('came_from', None)

plone_utils.addPortalMessage(pmf(u'Mail sent.'))
return state
