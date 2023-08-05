Introduction
============
The solely intention of this product is to show in Image and News Item content types an icon-toolbar viewlet in the plone.abovecontentbody viewlet manager.

By keeping the user in the same page and requiring less clicks and page loads we intend to ease applying transformations in the images.

This is an alternative to `collective.atimage.transformmenu <http://pypi.python.org/pypi/collective.atimage.transformmenu>`_.

Features
========

- Toolbar is in plone.abovecontentbody viewlet manager for Image and News Item
- Performs image transformations with AJAX to prevent reloading the page
- Degrades gracefully in non-JavaScript browsers
- i18n support by using atcontentypes and plone i18n domains.
- Tested in Plone 3.3.5 and Plone 4.0
- 'Transforms' tab is hidden in Image objects as its functionalities are now provided by the toolbar.
