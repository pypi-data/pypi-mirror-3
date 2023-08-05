.. contents::

Documentation
=============

.. image:: http://keul.it/images/plone/monet.mapsviewlet-0.5.0-02.png
   :alt: Monet Citypass preview
   :align: left
   :target: http://keul.it/images/plone/monet.mapsviewlet-0.5.0-01.png

Every Plone content can now display a Google's Map inside a viewlet. In the simpler use case the map is
centered on a valid address that Google Maps service can understand (like "*Piazza Grande, Modena, Italy*")
taken from the content's "*Location*" field.

The viewlet is placed (by default) below the content, but your custom theme can move it where you want.

To finally enable the map you need also to access a new option under the "*Action*" menu. Use this
same menu for disabling the map. Remember that a map is displayed only if there is a geolocation to
display; if not, a user with the proper permission only see a warning message while other users don't
see anything.

Advanced use
------------

.. image:: http://keul.it/images/plone/monet.mapsviewlet-0.6.0-02-mini.png
   :alt: Geolocation fieldset
   :align: right
   :target: http://keul.it/images/plone/monet.mapsviewlet-0.6.0-02.png

When you mark a content as "map enabled", you will see a new "*Geolocation*" fieldset when you edit it.

From this fieldset you can customize some map behaviors, like:

* you can choose to point the map onto a different point that isn't the content "Location" field (maybe
  still keeping the Location as the displayed baloon info).
* you can set the starting zoom level of the map
* you can choose to display or not the baloon on the marker, or display a custom text that isn't the
  Location 

If you don't provide an official Location but only the alternative Geolocation and choose to display
the location info, the displayed address will be reverse-geocoded, to display a human readable information.

Maps dependency
---------------

Starting from version 0.6, the product needs `Maps`__ as dependency. A lot of configuration procedures
(like put a valid `Google Key`__) are now left to Maps itself. Please refer to its documentation.

__ http://plone.org/products/maps
__ http://code.google.com/apis/maps/signup.html

In this way we also use the location field and widget for choose a geolocation directly using Google Maps.

Finally, a content that is "map enabled" and were you choosed a geolocation from the new field, can be used
as a Maps GeoLocation content (in Folder or Collection "Map view").

.. image:: http://keul.it/images/plone/monet.mapsviewlet-0.6.0-03-mini.png
   :alt: View of the menu entry
   :target: http://keul.it/images/plone/monet.mapsviewlet-0.6.0-03.png

KML
---

Also you can handle `KML`__ file using again the Google APIs.
You must simply add Plone files with KML extensions to the *related contents* section of a document
where the map is enabled.

__ http://code.google.com/apis/kml/documentation/whatiskml.html

When you have KML data to show, you can also use a new portlet that will help users to enable/disable
single KML data from the map. The portlet must be enabled where you prefer like every other.

.. Note::
   You can use and test KML features only with online site. When working locally all KML features simply
   don't work.

Other dependencies
==================

Tested on Plone 3.3 and 4.1 with `Products.Maps 2.1.1`__

__ http://plone.org/products/maps/releases/2.1.1

TODO and know issues
====================

* think about moving KML files away from using related contents and into the new geolocation fieldset
* make the *Products.Maps* dependency optional while keeping all other features
* find a more elegant way to fix `issue #35 of Maps`__ 
* find how to fix a `bug for using the LocationWidget on Firefox`__ (see also `Maps issue #36`__)
* some geolocation fieldset's elements are not translable (seems they are using the ``plone`` domain)

__ http://plone.org/products/maps/issues/35
__ http://permalink.gmane.org/gmane.comp.web.zope.plone.user/115279
__ http://plone.org/products/maps/issues/36

Other products
==============

If you need something more professional, pluggable and modular (also with KML support) don't miss the
`collective.geo`__ suite!
We suggent you to evaluate this suite for a modern Plone 4.0 and 4.1 environment. Still, Monet Maps Viewlet
is Plone 3 compatible.

__ http://plone.org/products/collective.geo/

Credits
=======

Developed with the support of:

* `Rete Civica Mo-Net - Comune di Modena`__
  
  .. image:: http://www.comune.modena.it/grafica/logoComune/logoComunexweb.jpg 
     :alt: Comune di Modena - logo
  
* `S. Anna Hospital, Ferrara`__

  .. image:: http://www.ospfe.it/ospfe-logo.jpg  
     :alt: S. Anna Hospital - logo

All of them supports the `PloneGov initiative`__.

__ http://www.comune.modena.it/
__ http://www.ospfe.it/
__ http://www.plonegov.it/

Authors
=======

This product was developed by RedTurtle Technology team.

.. image:: http://www.redturtle.it/redturtle_banner.png
   :alt: RedTurtle Technology Site
   :target: http://www.redturtle.it/

