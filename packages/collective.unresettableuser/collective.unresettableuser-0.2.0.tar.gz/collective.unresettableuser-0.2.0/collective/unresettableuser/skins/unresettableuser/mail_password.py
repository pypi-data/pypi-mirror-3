## Script (Python) "mail_password"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##title=Mail a user's password
##parameters=

from Products.CMFPlone import PloneMessageFactory as _
REQUEST=context.REQUEST
try:
    userid = REQUEST['userid']
    # test the block user password
    mtool = context.portal_membership
    member = mtool.getMemberById(userid)
    if member and member.getProperty('block_password_reset'):
        context.plone_utils.addPortalMessage(_(u"This user can't reset his password"), type='error')
        response = context.mail_password_form()
        return response
    response = context.portal_registration.mailPassword(userid, REQUEST)
except ValueError, e:
    context.plone_utils.addPortalMessage(_(str(e)))
    response = context.mail_password_form()
return response
