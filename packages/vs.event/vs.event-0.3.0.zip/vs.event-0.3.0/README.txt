vs.event
========

``vs.event`` provides an extended event functionality for Plone

Features
========

- recurring events
- a new calendar widget 
- real support for all-day events
- extended support for attendees and attachments (UI and iCal level)
- working iCal/vCal export for all-day events
- full integration with Plone4Artists calendar (must be installed seperately)
- support for supplementary-events (one master event and several depending events)

Supplementary events
====================

There are case where some particular event in reality consists of several date.
E.g. for conference  you need an event for the conference date itself. However
you often have additional supplementary events like a deadline for a
call-for-papers or a registration deadline. With ``vs.event`` you create an
event for the conference itself and so-called ``supplementary events`` for the
call-for-papers and the registration deadline. The supplementary dates are
events themselves but linked with the primary event (using the Archetypes
references). So with ``vs.event`` you will see all supplementary events for the
main event or jump directly from a supplementary event to its main event.  This
feature is optional and can be disabled through the ZMI in portal_calendar ->
vs_event_supplementary_events.

Integration with Plone4Artists calendar
=======================================

``vs.event`` integrates smoothly with ``p4a.plonecalendar``. A new view
``icalendar_export`` is registered for p4a.plonecalendar enabled folders.  It
will export all ``vs.event`` related events in iCal. This means you can
subscribe with iCal to a calendar taking full advantage of the `vs.event``
functionality (including support for attachments and attendees on the iCal
level).

Installation
============

Add ``vs.event`` to the ``eggs`` and ``zcml`` options of your buildout.cfg.
Create a new Plone site using the ``vs.event`` profile or install ``vs.event``
through the quick installer of Plone.

Known bugs and limitations
==========================

- the localization of the date picker widget support only 'en' and 'de'
  so far. The date picker widget will use/present the US date format for
  languages other than German.

TODO
====

- more i18n needed

License
=======

``vs.event`` is published under the GNU Public License 2.

Parts of the code of ``vs.event`` (iCal implementation) are based on work
in ATContentTypes.

Authors
=======

- Andreas Jung
- Veit Schiele
- Anne Walther

Repository
==========

http://svn.plone.org/svn/collective/vs.event

Contact
=======

Send mail to vs.event@veit-schiele.de
