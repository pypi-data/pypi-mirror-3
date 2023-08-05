Introduction
============

This product is a replacement of the basic Plone Event content type.

Is the main part of the `monet.calendar.star`__ suite, but you can use it freely as indipendent product.

__ http://plone.org/products/monet.calendar.star

It provides a lot of additional field, developed for the *City of Modena* public event management
system.
Apart new content data, and an image field, you can now choose:

* `Cadence` - weekdays where the event really happen
* `Except` - specific days where the event *is not* available
* `Including` - specific days where the event *is* available (apart from other filters)
* ...other

.. figure:: http://keul.it/images/plone/monet.calendar.event-0.3.0-01.png
   :alt: Part of the edit form

   Some of the new fields in the event editing form

Also, the "*event type*" field is now a closed list of values (see below for customization). 

Configuration
-------------

From ZMI you need to customize the *event_types* property inside the *monet_calendar_event_properties*
property sheet.

Features
--------

Used as it is, all the recurring information are no more that data inside the content. Please see
the  `Monet Calendar suite`__ for knowing how to use it.

__ http://plone.org/products/monet.calendar.star

Warning
-------

This product replace the Plone basic Event content type. You can still continue using old Events, but
additional fields will be available only for future contents.

Dependencies
============

For "Except" days selection, `rt.calendarinandout`__ widget is needed

__ http://pypi.python.org/pypi/rt.calendarinandout

Plone 3.3 or better is needed.

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

  .. image:: http://www.provincia.fe.it/Distribuzione/logo_provincia.png
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

.. image:: http://www.redturtle.it/redturtle_banner.png
   :alt: RedTurtle Technology Site
   :target: http://www.redturtle.it/
