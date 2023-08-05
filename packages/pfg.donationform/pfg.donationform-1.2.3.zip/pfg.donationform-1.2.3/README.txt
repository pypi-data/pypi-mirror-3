Introduction
============

This package streamlines the process of creating a donation form within a Plone
site that can process payments via one of the payment processors supported by
`PloneGetPaid`_.

.. _`PloneGetPaid`: http://plonegetpaid.com

On its own, `PloneGetPaid`_ provides a useful basis for processing electronic
payments within Plone, including support for a number of payment processors.
However, PloneGetPaid is optimized for the use case of purchasing products, and
makes some assumptions that are suboptimal for collecting donations:

* It assumes that any item purchased is represented by a content item within the
  site, which is not the case for arbitrary donations.
* It provides no user interface for selecting among predefined donation levels -or-
  entering an arbitrary donation amount.
* Its checkout process requires several steps, whereas making a donation should
  be as streamlined as possible.

pfg.donationform solves these problems by creating a `PloneFormGen`_-based donation
form with a custom "donation field" that provides an acceptable UI for configuring
a donation amount and recurring donation.  When the form is submitted, it can
either process the donation immediately based on contact and billing fields
included in the form, or can redirect to the standard GetPaid checkout wizard.

.. _`PloneFormGen`: http://plone.org/products/ploneformgen

The donation field may also be used in other PloneFormGen forms.

Dependencies
------------

pfg.donationform works on both Plone 3 and Plone 4.  Recent versions of
PloneFormGen and PloneGetPaid are required.

Installation
------------

Add GetPaid to your buildout, using the instructions at
http://code.google.com/p/getpaid/wiki/InstallingGetPaid to make sure you get
the correct package versions.

Add pfg.donationform to your buildout.

Start Zope and install PloneGetPaid via the Add-ons control panel, and configure
its settings.

Install "Donation Form" via the Add-ons control panel.

Make sure you have configured your Plone site's mailhost settings.

Usage
-----

Begin adding a donation form by selecting "Donation Form" from Plone's
Add menu.  Fill out the fields and click "Add" to finish adding the form.

By default GetPaid uses a dummy payment processor that "accepts" payment
without actually doing anything.  You will need to configure GetPaid via its
control panel in Site Setup.

Customization
-------------

Because the generated form is a PloneFormGen form, you may edit or add fields
via the normal PloneFormGen user interface.  If you add a field and want it to
be included in the e-mail that is sent when a donation is made, you must also
edit the mailer adapter and add it to the list of included fields.  (All fields
are not included automatically, in order to avoid sending sensitive credit card
information via e-mail.)

If you let the Donation Form creation process add contact and billing fields to
the form, make sure that you do not remove them or change their IDs -- the
GetPaid adapter expects to find them.

Credits
-------

pfg.donationform was created for `Groundwire`_ by `David Glick`_.  Thanks also
to Fulvio Casali.

.. _`Groundwire`: http://groundwire.org
.. _`David Glick`: http://davisagli.com
