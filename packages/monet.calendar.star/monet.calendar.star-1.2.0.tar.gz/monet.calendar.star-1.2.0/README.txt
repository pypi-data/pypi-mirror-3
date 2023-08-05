.. contents::

Introduction
============

The *Monet Calendar* suite (also *monet.calendar.star*) is a complete event managing solution for Plone,
inspired by needs of the `City of Modena`__. Is widely used there for managing all kind of events.

__ http://www.comune.modena.it/

This is only a transitional package, for downloading and installing all other products in the suite
in a simple way.

Features
========

We want to give to Plone an event type that:

* hide totally the "time" data (managed as simple text)
* give a closed (but configurable) set of type of events
* the days of weeks where really the event take place
* be able to manage special days where the event *don't* take place
* a lot of additional text information
* an advanced search feature

See the `monent.calendar.event page`__ for know how to configure the event.

__ http://pypi.python.org/pypi/monet.calendar.event

Searching events
----------------

Additionally one (at least) or more Plone folders can be marked as "*Calendar section*" in a new "Calendar" menu.

.. figure:: http://keul.it/images/plone/monet.calendar.suite-1.0.0-01.png
   :alt: The new Calendar menu

   Entries inside the new "Calendar menu"

This mean that this folder can use the "*Calendar view*" that show events in the current day, taken
(by default, see below) from all the site events. This search take care of counting exceptions and
days of the week of events.

.. figure:: http://keul.it/images/plone/monet.calendar.suite-1.0.0-02.png
   :alt: Single day view

   The "Calendar view"

Every event (and the also calendar sections) will also show a new "search" section at the top. This
form can be used to perform a search on events of the calendar.

.. figure:: http://keul.it/images/plone/monet.calendar.suite-1.0.0-03.png
   :alt: As new events looks like

   The search form on events

The form can be used to expand the search to more than one day, showing a summary of all events, per-day

.. figure:: http://keul.it/images/plone/monet.calendar.suite-1.0.0-04.png
   :alt: Search results on multiple days

   Search results on multiple days

Use multiple calendar: "Calendar root" sections
-----------------------------------------------

Using again the "*Calendar menu*" you can also mark folders as "Calendar root".
This is useful when using a Plone filled of subsites, where you can have a *main calendar* that
look at every event in the site, but also additional sub-calendars (inside many calendar roots).

When a calendar perform searches inside a Calendar root, it will only look for events inside the
calendar root itself.

A calendar outside a Calendar root looks for all events in the site.

.. figure:: http://keul.it/images/plone/monet.calendar.suite-1.0.0-05.png
   :alt: Search results on multiple days

   Same search above, but on a local calendar
   ("Subsite 1" there is a "Calendar root" section)

New calendar portlet
--------------------

The calendar construction is expensive, and not good to be used in a portlet of the site, where is
visible (in the worst case, also not cached) in every page of the site.

When you install the monet.calendar.extension product, the calendar portlet is replaced with a version
that:

* not show anymore events in a specific day
* every cell is a link that perform a day-search in the nearest calendar

"*Nearest calendar*" mean that if the visitor is inside a "calendar root" section he will be moved to
the calendar of that section, otherwise a global calendar section will be used.

You can also install an additional portlet from the `monet.calendar.portlet`__ product. This portlet 
gives you a way to select a calendar section in the site, then display it in a portlet (in the same way
you can see him in the calendar section itself).

__ http://pypi.python.org/pypi/monet.calendar.portlet

.. Note::
   The portlet is designed to be used with `collective.portletpage`__. Using it in a narrow column portlet
   must be fixed by your Plone theme!

__ http://pypi.python.org/pypi/collective.portletpage

New collection criteria
-----------------------

You can use the `monet.calendar.criteria`__ for beeing able to create collection that looks for events
taking care of event's filters parameter.

__ http://pypi.python.org/pypi/monet.calendar.criteria

Special event types
-------------------

From ZMI (see also `monet.calendar.event`__ configuration) you can specify one or more event type
as "special". Those are then highlighted in the single day view, below the categorizations done for
the time of event.

__ http://pypi.python.org/pypi/monet.calendar.event

Examples:

* Morning
* Afternoon
* Evening
* *YouEventType*

Dependencies tree
=================

You can freely install single components of the suite, that are:

* monet.calendar.event

  * rt.calendarinandout

    * collective.js.jqueryui

* monet.calendar.extensions

* monet.calendar.portlet (optional, see above)

* monet.calendar.criteria

* monet.calendar.location (optional, and not covered by this package.
  It contains Modena's and italian specific patch... you probably don't need this. Really)

Requirements
============

The monet.calendar.star solution works onto:

* Plone 3.3
* Plone 4
* Plone 4.1

Migrating from older release
============================

If you have a Plone site where you used and old version of ``monet.calendar.event`` (older than 0.4)
you probably need to add to your buildout the historical `monet.recurring_event`__ (0.7 or better.)

__ http://pypi.python.org/pypi/monet.recurring_event/0.7.0

Credits
=======
  
Developed with the support of:

* `Rete Civica Mo-Net - Comune di Modena`__

  .. image:: http://www.comune.modena.it/grafica/logoComune/logoComunexweb.jpg 
     :alt: Comune di Modena - logo

* `Provincia di Ferrara`__

  .. image:: http://people.provincia.fe.it/people/img/logo_provincia.png
     :alt: Provincia di Ferrara - logo

* `Regione Emilia Romagna`__

All of them supports the `PloneGov initiative`__.

__ http://www.comune.modena.it/
__ http://www.provincia.fe.it/
__ http://www.regione.emilia-romagna.it/
__ http://www.plonegov.it/

Authors
=======

This product was developed by RedTurtle Technology team.

.. image:: http://www.redturtle.net/redturtle_banner.png
   :alt: RedTurtle Technology Site
   :target: http://www.redturtle.net/

