.. contents::


Introduction
============

Products.SimpleReference is an addon for Products.RichDocument to enable
Image/File referencing. Image/File referencing gives you the ability to leave
Image/File data at one defined place in your Plone site and therefore you
prevent having duplicate data for each RichDocument.

SimpleReference adds two new types "ImageReference" and "FileReference"
and overrides the widget templates of Products.SimpleAttachment to add these
References via kss enabled viewlet.

Overriding SA templates is done because you are now able to sort ImageAttachments
and ImageReferences (or FileAttachments, FileReferences) in one place.



This Plone Addon was developed by `Kombinat Media Gestalter GmbH`_.

.. image:: http://kombinat.at/kombinat-logo.gif
   :target: http://kombinat.at


For more information please visit our website. You can have a look into the
source by browsing the `svn repository`_.

.. _`svn repository`: https://svn.plone.org/svn/collective/Products.SimpleReference
.. _`Kombinat Media Gestalter GmbH`: http://kombinat.at
