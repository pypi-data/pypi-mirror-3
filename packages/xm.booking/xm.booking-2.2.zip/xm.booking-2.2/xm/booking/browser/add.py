from Acquisition import aq_inner
from kss.core import kssaction
from plone.app.kss.plonekssview import PloneKSSView
from Products.Five.browser import BrowserView
from viewlets import Bookings as BookingsViewlet
from viewlets import BookingForm as BookingFormViewlet
from DateTime import DateTime


def create_booking(context, title='Booking', hours=0, minutes=0,
                   description=u'',
                   day=None):
    """Create a booking.

    We introduce a Mock Booking class for testing.

    >>> class MockBooking(object):
    ...     def __init__(self, **kwargs):
    ...         for key, value in kwargs.items():
    ...             self.__setattr__(key, value)
    ...     def unmarkCreationFlag(self):
    ...         pass

    Let's try this.

    >>> booking1 = MockBooking(id=42, blah='h2g2')
    >>> booking1.id
    42
    >>> booking1.blah
    'h2g2'
    >>> booking1.title
    Traceback (most recent call last):
    ...
    AttributeError: 'MockBooking' object has no attribute 'title'


    For now Bookings are added in Tasks, so we create a Mock Task
    class.

    >>> class MockTask(object):
    ...     def __init__(self):
    ...         self.items = {}
    ...         self.next_id = 1
    ...     def invokeFactory(self, type, **kwargs):
    ...         if type != 'Booking':
    ...             raise Exception('We want only Bookings.')
    ...         booking_id = str(self.next_id)
    ...         self.next_id += 1
    ...         self.items[booking_id] = MockBooking(**kwargs)
    ...         return booking_id
    ...     def objectIds(self):
    ...         return self.items.keys()
    ...     def get(self, id):
    ...         return self.items.get(id)
    >>> context = MockTask()
    >>> context.objectIds()
    []
    >>> context.invokeFactory('Solfatara')
    Traceback (most recent call last):
    ...
    Exception: We want only Bookings.


    XXX We may want to put these Mocks and their tests into another
    class that we can use in other places as well.

    Try a few stupid things.

    >>> create_booking()
    Traceback (most recent call last):
    ...
    TypeError: create_booking() takes at least 1 argument (0 given)
    >>> create_booking(context, id='Peroni')
    Traceback (most recent call last):
    ...
    TypeError: create_booking() got an unexpected keyword argument 'id'

    Right, the basics seem to work.  Now we go and create some
    Bookings with this function.  We have some defaults in place.

    >>> create_booking(context)
    >>> context.objectIds()
    ['1']
    >>> booking = context.get('1')
    >>> booking.title
    'Booking'
    >>> booking.hours
    0
    >>> booking.minutes
    0

    Now add some non default values.

    >>> create_booking(context, title='Buongiorno', hours=3, minutes=15)
    >>> context.objectIds()
    ['1', '2']
    >>> booking = context.get('2')
    >>> booking.title
    'Buongiorno'
    >>> booking.hours
    3
    >>> booking.minutes
    15

    By default the description is empty, but optionally we can supply
    one.

    >>> booking.description
    u''
    >>> create_booking(context, title='Title', description=u'A description.')
    >>> booking = context.get('3')
    >>> booking.description
    u'A description.'

    We can supply a day on which to book. The default is today. Note that
    below checks will fail when executed at exactly midnight... ;-)

    >>> today = str(DateTime())[:10]
    >>> str(booking.bookingDate)[:10] == today
    True
    >>> create_booking(context, title='Title', day=DateTime('1972-12-25'))
    >>> booking = context.get('4')
    >>> booking.bookingDate
    DateTime('1972/12/25')

    """

    if day == None:
        day = DateTime()
    idx = 1
    while str(idx) in context.objectIds():
        idx = idx + 1
    # Add the booking and get the generated id, as theoretically this
    # might differ from what we ask.
    booking_id = context.invokeFactory(
        'Booking', id=str(idx), title=title,
        hours=hours, minutes=minutes,
        description=description, bookingDate=day)
    obj = context.get(booking_id)
    obj.unmarkCreationFlag()


class Create(BrowserView):

    def __call__(self):
        form = self.request.form
        title = form.get('title', '')
        hours = form.get('hours', 0)
        minutes = form.get('minutes', 0)
        context = aq_inner(self.context)
        create_booking(context, title=title, hours=hours, minutes=minutes)
        self.request.response.redirect(context.absolute_url())


class Add(PloneKSSView):

    @kssaction
    def add_booking(self):
        # We *really* need the inner acquisition chain for context
        # here.  Otherwise the aq_parent is the view instead of the
        # story, which means the totals for the story are not
        # recalculated.  Sneaky! :)
        context = aq_inner(self.context)
        create_booking(context, title=self.request.form.get('title'),
                       hours=self.request.get('hours'),
                       minutes=self.request.get('minutes'))
        core = self.getCommandSet('core')

        # Refresh the booking table
        viewlet = BookingsViewlet(context, self.request, None, None)
        viewlet.update()
        rendered = viewlet.render()
        selector = core.getHtmlIdSelector('booking-table')
        core.replaceHTML(selector, rendered)

        # Refresh the add booking form
        viewlet = BookingFormViewlet(context, self.request, None, None)
        viewlet.update()
        rendered = viewlet.render()
        selector = core.getHtmlIdSelector('add-booking')
        core.replaceHTML(selector, rendered)
