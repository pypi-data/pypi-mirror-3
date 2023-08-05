Introduction
============

Press Room is a simple add-on product which can be used to easily manage an
online Press Room within your Plone site.  It adds 4 new content types to your
Plone site including a Press Release, a Press Clip (i.e. an outside news
piece), and a Press Contact (someone who might be available to speak to the
press.)

It also provides a Press Room, a folderish content type with a nice default
view and some automatically created folders and Collections (aka Smart Folders)
to help you organize and present your press materials.

Some press rooms we observed in making this product are found at microsoft.com,
intel.com, nrdc.org, sierraclub.org, and google.com.  Our goal was to make
something suitable for many kinds of organizations, including nonprofits,
businesses, educational institutions, and more.

Features
========

Press Releases
--------------

    * Headline
    * Subheadline
    * Release date & timing
    * Location
    * Image
    * Related press contacts (see below)
    * Related content items elsewhere on your site

Press Clips
-----------

Published media stories about your organization or of general interest.

    * Date of story
    * Publication
    * Reporter
    * Excerpted text
    * Hyperlink to original story

Press Contacts
--------------

People with whom reporters can follow up. Press Contacts can be associated
with Press Releases.

    * Name
    * Description
    * Job Title
    * Email Address
    * City
    * State/Province
    * Organization
    * Phone number

Press Room provides a master "Press Room" view showing a configurable number
of Releases, Clips and Contacts (any of which can also be hidden).

Press Room also makes available RSS feeds of Press Releases and Press Clips.

Press Rooms in Action
=====================

    * `People for Puget Sound`_
    * `Conservation Northwest`_
    * `Sierra Club of BC`_
    * `Ecojustice Canada`_

.. _`People for Puget Sound`: http://www.pugetsound.org/pressroom
.. _`Conservation Northwest`: http://www.conservationnw.org/pressroom
.. _`Sierra Club of BC`: http://www.sierraclub.bc.ca/quick-links/media-centre
.. _`Ecojustice Canada`: http://www.ecojustice.ca/media-centre

Current Status of Press Room
============================

This release of PressRoom has been tested with Plone 2.5.5, Plone 3.3.2, and
Plone 4.0b1. We assume it will work for most Plone releases 2.5 through 4.0b1.
If you have a Plone 2.1 site, please see the PressRoom 1.1 line.  We are
committed to supporting the two most current Plone releases at a time.

Known bugs and issues are listed at http://plone.org/products/pressroom/issues

Suggestions welcome!  (Code even more welcome!)

Roadmap: http://plone.org/products/pressroom/roadmap

Installation
============

Install in the usual way, by:

 * Adding the Products.PressRoom egg to your buildout
 * Browse to your plone site --> site setup --> add/remove products
 * Click install (or you can use the QuickInstaller tool in the Zope Management Interface)

Usage
=====

We recommend creating a Press Room object in the root of your site.
Then begin creating Press Releases, Press Clips and Press Contacts in your
Press Room.  
 
The "Add Press (item)" links in the Press Room will shortcut you to subfolders
intended to store these items.  Only items stored in their appropriate
subfolder will be shown in the Press Room view.
 
You may create Press Releases, Clips and Contacts elsewhere in your site, but
these will not be shown in the Press Room view.
 
You might find it useful to suppress the ability to add normal News Items if
Press Room replaces that need.  You can do that by going into the portal_types
tool in the ZMI and unchecking "implicitly addable" for News Items.

Note that in Plone 3.0+, the infrastructure supporting each Press Room by
default is created as "private".  The Press Room provides a button to publish
all of these.  That button will NOT publish any actual Releases, Clips or
Contacts -- just the folders that contain them and the Collections that
aggregate them.

Upgrading Folders
=================

As of Press Room 3.2, the containers for Press Clips and Press Releases are
Large Plone Folders. Before 3.2, Press Room used normal folders, which become
inefficient when containing more than about a hundred items.  To upgrade an
older Press Room, navigate to the Press Room and append "/@@upgrade-folders" to
the url. A message will return with the results of the upgrade. Note that your
Press Room subfolders must retain their original ids ('press-clips' and
'press-releases') in order to be upgraded.

Note also that, by default, Large Plone Folders are not normally addable in a
Plone site. To allow the creation of the two used in a new Press Room, we
briefly enable them (if they weren't already) and after adding them, we disable
them again. That means that attempts to rename them will cause a cryptic error
about disallowed types. To get around that, simply navigate to portal_types in
the ZMI, click into Large Plone Folders, and check the "Implicitly addable"
checkbox.

In Plone 4, standard folders are BTree-based and can better handle large numbers
of items, so Large Plone Folders are no longer used.  Folders that were already
upgraded to Large Plone Folders in Plone 3 can remain that way.
