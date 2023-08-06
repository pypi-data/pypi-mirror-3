History of xm.booking
=====================

2.2 (2012-09-12)
----------------

- Moved to github.
  [maurits]


2.1 (2011-02-03)
----------------

- Added missing return statement in the size_estimate indexer.
  You may want to recatalog the Stories to fix their size_estimate.
  [maurits]


2.0 (2010-09-24)
----------------

- Made booking table compatible with both Plone 3 and 4, by using
  either poi_niceName (Plone 3, Poi 1.2) or @@pas_member (Plone4).
  [maurits]

- Explicitly load the permissions.zcml file from
  Products.eXtremeManagement, otherwise you might get a
  ComponentLookupError on zope startup.
  [maurits]

- Added z3c.autoinclude.plugin target plone.
  [maurits]

- Use plone.indexer instead of the deprecated
  registerIndexableAttribute which no longer works in Plone 4.  Added
  dependency on plone.indexer for this, so using Plone 3.3 is
  recommended (might still work on earlier versions).
  [maurits]


1.1 (2010-05-01)
----------------

- Avoid renaming bookings that were added via the tracker at the
  moment you edit them.
  Fixes http://plone.org/products/extreme-management-tool/issues/184
  [maurits]


1.0 (2009-05-05)
----------------

- Protect the booking table with the eXtremeManagement: View Details
  permission.  [maurits+mike]


0.9 (2009-01-25)
----------------

- Nothing changed yet.


0.8 (2009-01-07)
----------------

- Nothing changed yet.


0.7 (2008-10-06)
----------------

- Fixed error where a day=DateTime() default argument in a method defintion
  would get stuck with the DateTime() of the moment when the site was last
  started, sigh. KSS-added bookings all got that date. Fixes
  http://plone.org/products/extreme-management-tool/issues/80. [reinout]


0.6 (2008-09-16)
----------------

- Added optional argument 'description' to create_booking.  [maurits]

- Showing booking's description as 'structure' as it is handled as
  webintelligent text in Products.eXtremeManagement's views now. [reinout]


0.5 (2008-03-04)
----------------

- No history recorded.


0.4 (2008-03-04)
----------------

- No history recorded.


0.3 (2008-02-25)
----------------

- No history recorded.
