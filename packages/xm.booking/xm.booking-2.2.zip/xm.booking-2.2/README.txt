xm.booking
==========

This is a package for booking hours on a content type.  It also
handles estimates of duration or size.  It is a spin-off from
eXtremeManagement.  Quite likely some more code needs to move between
those two.

xm.booking is intended to be useful without eXtremeManagement.  But
for now the bookings from Products.eXtremeManagement.content.Bookings
are used.  In place of that we want to make a nice and small Zope 3
content object.  Of course this needs migration code in
eXtremeManagement.

Conversely, eXtremeManagement depends on xm.booking, so if you change
this package, please also run the eXtremeManagement tests.  If unsure,
please contact the eXtremeManagement authors or mailing list.  See
http://plone.org/products/extreme-management-tool/

The code is hosted at https://github.com/zestsoftware/xm.booking
