Introduction
============

This is a full-blown functional test. The emphasis here is on testing what
the user may input and see, and the system is largely tested as a black box.
We use PloneTestCase to set up this test as well, so we have a full Plone site
to play with. We *can* inspect the state of the portal, e.g. using 
self.portal and self.folder, but it is often frowned upon since you are not
treating the system as a black box. Also, if you, for example, log in or set
roles using calls like self.setRoles(), these are not reflected in the test
browser, which runs as a separate session.

Being a doctest, we can tell a story here.

First, we must perform some setup. We use the testbrowser that is shipped
with Five, as this provides proper Zope 2 integration. Most of the 
documentation, though, is in the underlying zope.testbrower package.

    >>> from Products.Five.testbrowser import Browser
    >>> browser = Browser()
    >>> portal_url = self.portal.absolute_url()

The following is useful when writing and debugging testbrowser tests. It lets
us see all error messages in the error_log.

    >>> self.portal.error_log._ignored_exceptions = ()

With that in place, we can go to the portal front page and log in. We will
do this using the default user from PloneTestCase:

    >>> from Products.PloneTestCase.setup import portal_owner, default_password

    >>> browser.open(portal_url + '/login_form')

Here, we set the value of the fields on the login form and then simulate a
submit click.

    >>> browser.getControl(name='__ac_name').value = portal_owner
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()


And we ensure that we get the friendly logged-in message:

    >>> "You are now logged in" in browser.contents
    True

Image content type
===============================
    >>> browser.open(self.image.absolute_url() + '/view')

Now we test the Transform toolbar
Given that this product hides the "Transform" content-view tab, we should get an error when getting the "Transform" tab link

    >>> browser.getLink('Transform')
    Traceback (most recent call last):
    ...
    LinkNotFoundError

In spite, there should be a Transform label present in page

    >>> '<span class="label">Transform</span>' in browser.contents
    True

Now we make sure we are in the 'View' tab of the Image before transforming the image in any possible way, to end up in the same View page
    >>> browser.getLink('View').click()
    >>> view_url = browser.url
    >>> browser.contents
    '...<img src="http://nohost/plone/image/image_preview" ... height="56" width="215" />...'
    >>> browser.getLink('Flip around vertical axis').click()
    >>> browser.getLink('Flip around horizontal axis').click()
    >>> browser.getLink('Rotate 90 counterclockwise').click()
    >>> browser.contents
    '...<img src="http://nohost/plone/image/image_preview"...height="215" width="56" />...'
    >>> browser.getLink('Rotate 180').click()
    >>> browser.getLink('Rotate 90 clockwise').click()
    >>> browser.contents
    '...<img src="http://nohost/plone/image/image_preview"...height="56" width="215" />...'
    >>> browser.url == view_url
    True
    
Try AJAX transformations
First we try an available transformation::

    >>> transform_link = browser.getLink('Flip around vertical axis')
    >>> browser.open(transform_link.url + '&ajax=1')
    >>> browser.headers['content-type']
    'application/json; charset=utf-8'
    >>> browser.contents
    '{"success": true}'
    
Now we try a non-existing transformation (by adding 00 to the last parameter of the URL) ::    
    >>> browser.open(view_url)
    >>> transform_link = browser.getLink('Flip around horizontal axis')
    >>> browser.open(transform_link.url + '00&ajax=1')
    >>> browser.headers['content-type']
    'application/json; charset=utf-8'
    >>> browser.contents
    '{"success": false, "error": {"...'
    
News Item with image
===============================

    >>> browser.open(self.newsitemwithimage.absolute_url() + '/view')
    >>> view_url = browser.url

Original image is displayed

    >>> browser.contents
    '...<div class="newsImageContainer">...<a href="http://nohost/plone/with-image/image/image_view_fullscreen"...<img src="http://nohost/plone/with-image/image_mini" ... height="52" width="200"...'


Then, we click on every transformation option in the menu (testing that some specific transformations)
really transform the image.
And we finally get to the same original view url.

    >>> browser.getLink('Flip around vertical axis').click()
    >>> browser.getLink('Flip around horizontal axis').click()
    >>> browser.getLink('Rotate 90 counterclockwise').click()
    >>> browser.contents
    '...<img src="http://nohost/plone/with-image/image_mini" ... height="200" width="52"...'
    >>> browser.getLink('Rotate 180').click()
    >>> browser.getLink('Rotate 90 clockwise').click()
    >>> browser.contents
    '...<img src="http://nohost/plone/with-image/image_mini" ... height="52" width="200"...'
    >>> browser.url == view_url
    True

News Item without image
===============================

In a News Item without image 'Transform' menu and its subitems are not present.
    
    >>> browser.open(self.newsitemnoimage.absolute_url())
    >>> browser.getLink(url='@@transform?method:int=')
    Traceback (most recent call last):
    ...
    LinkNotFoundError


Page (ATDocument)
===============================

In a Page object 'Transform' menu and its subitems are not present.
    
    >>> browser.open(self.doc.absolute_url())
    >>> browser.getLink(url='@@transform?method:int=')
    Traceback (most recent call last):
    ...
    LinkNotFoundError
