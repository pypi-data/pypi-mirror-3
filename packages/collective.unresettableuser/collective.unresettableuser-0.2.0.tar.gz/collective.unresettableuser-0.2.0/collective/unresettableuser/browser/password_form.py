# -*- coding: utf-8 -*-

from AccessControl import Unauthorized
from zope.interface import Interface
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

class IPasswordFormView(Interface):
    
    def can_reset_my_password():
        """Check if the current user has the block_password_reset flag, and raise
        Unauthorized if True"""


class PasswordFormView(BrowserView):
    """View for checking security of the reset user password"""
    
    def can_reset_my_password(self):
        member = getToolByName(self.context, 'portal_membership').getAuthenticatedMember()
        if member.getProperty('block_password_reset'):
            raise Unauthorized("You can't reset this user's password")
        return False