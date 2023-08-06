from Acquisition import aq_inner
from plone.app.layout.viewlets import ViewletBase
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from zope.interface import Interface
from zope.interface import implements


class BookingFormInterface(Interface):

    def allowed():
        """Is the user allowed to add a booking here?
        """
        pass


class Bookings(ViewletBase):

    render = ViewPageTemplateFile("bookingtable.pt")


class BookingForm(ViewletBase):
    implements(BookingFormInterface)

    # Apparently this is needed to give access to the 'allowed'
    # attribute in case this viewlet gets rendered within a KSS view
    # (while adding a booking using this form), which messes up the
    # Acquisition chain or something...
    __allow_access_to_unprotected_subobjects__ = 1

    def allowed(self):
        """Is the user allowed to add a booking here?
        """
        context = aq_inner(self.context)
        mem = getToolByName(context, 'portal_membership')
        return mem.checkPermission('eXtremeManagement: Add Booking', context)

    render = ViewPageTemplateFile("add.pt")
