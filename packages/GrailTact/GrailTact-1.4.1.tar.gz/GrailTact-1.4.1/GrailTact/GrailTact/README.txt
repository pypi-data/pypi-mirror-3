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

Because add-on themes or products may remove or hide the login portlet, this test will use the login form that comes with plone.  

    >>> browser.open(portal_url + '/login_form')
    >>> browser.getControl(name='__ac_name').value = portal_owner
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()

Here, we set the value of the fields on the login form and then simulate a
submit click.  We then ensure that we get the friendly logged-in message:

    >>> "You are now logged in" in browser.contents
    True

Finally, let's return to the front page of our site before continuing

    >>> browser.open(portal_url)

-*- extra stuff goes here -*-
The Contact workplace and work title content type
===============================

In this section we are tesing the Contact workplace and work title content type by performing
basic operations like adding, updadating and deleting Contact workplace and work title content
items.

Adding a new Contact workplace and work title content item
--------------------------------

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

Then we select the type of item we want to add. In this case we select
'Contact workplace and work title' and click the 'Add' button to get to the add form.

    >>> browser.getControl('Contact workplace and work title').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'Contact workplace and work title' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'Contact workplace and work title Sample'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

And we are done! We added a new 'Contact workplace and work title' content item to the portal.

Updating an existing Contact workplace and work title content item
---------------------------------------

Let's click on the 'edit' tab and update the object attribute values.

    >>> browser.getLink('Edit').click()
    >>> browser.getControl(name='title').value = 'New Contact workplace and work title Sample'
    >>> browser.getControl('Save').click()

We check that the changes were applied.

    >>> 'Changes saved' in browser.contents
    True
    >>> 'New Contact workplace and work title Sample' in browser.contents
    True

Removing a/an Contact workplace and work title content item
--------------------------------

If we go to the home page, we can see a tab with the 'New Contact workplace and work title
Sample' title in the global navigation tabs.

    >>> browser.open(portal_url)
    >>> 'New Contact workplace and work title Sample' in browser.contents
    True

Now we are going to delete the 'New Contact workplace and work title Sample' object. First we
go to the contents tab and select the 'New Contact workplace and work title Sample' for
deletion.

    >>> browser.getLink('Contents').click()
    >>> browser.getControl('New Contact workplace and work title Sample').click()

We click on the 'Delete' button.

    >>> browser.getControl('Delete').click()
    >>> 'Item(s) deleted' in browser.contents
    True

So, if we go back to the home page, there is no longer a 'New Contact workplace and work title
Sample' tab.

    >>> browser.open(portal_url)
    >>> 'New Contact workplace and work title Sample' in browser.contents
    False

Adding a new Contact workplace and work title content item as contributor
------------------------------------------------

Not only site managers are allowed to add Contact workplace and work title content items, but
also site contributors.

Let's logout and then login as 'contributor', a portal member that has the
contributor role assigned.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url + '/login_form')
    >>> browser.getControl(name='__ac_name').value = 'contributor'
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

We select 'Contact workplace and work title' and click the 'Add' button to get to the add form.

    >>> browser.getControl('Contact workplace and work title').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'Contact workplace and work title' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'Contact workplace and work title Sample'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

Done! We added a new Contact workplace and work title content item logged in as contributor.

Finally, let's login back as manager.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url + '/login_form')
    >>> browser.getControl(name='__ac_name').value = portal_owner
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)


The Contact phone number content type
===============================

In this section we are tesing the Contact phone number content type by performing
basic operations like adding, updadating and deleting Contact phone number content
items.

Adding a new Contact phone number content item
--------------------------------

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

Then we select the type of item we want to add. In this case we select
'Contact phone number' and click the 'Add' button to get to the add form.

    >>> browser.getControl('Contact phone number').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'Contact phone number' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'Contact phone number Sample'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

And we are done! We added a new 'Contact phone number' content item to the portal.

Updating an existing Contact phone number content item
---------------------------------------

Let's click on the 'edit' tab and update the object attribute values.

    >>> browser.getLink('Edit').click()
    >>> browser.getControl(name='title').value = 'New Contact phone number Sample'
    >>> browser.getControl('Save').click()

We check that the changes were applied.

    >>> 'Changes saved' in browser.contents
    True
    >>> 'New Contact phone number Sample' in browser.contents
    True

Removing a/an Contact phone number content item
--------------------------------

If we go to the home page, we can see a tab with the 'New Contact phone number
Sample' title in the global navigation tabs.

    >>> browser.open(portal_url)
    >>> 'New Contact phone number Sample' in browser.contents
    True

Now we are going to delete the 'New Contact phone number Sample' object. First we
go to the contents tab and select the 'New Contact phone number Sample' for
deletion.

    >>> browser.getLink('Contents').click()
    >>> browser.getControl('New Contact phone number Sample').click()

We click on the 'Delete' button.

    >>> browser.getControl('Delete').click()
    >>> 'Item(s) deleted' in browser.contents
    True

So, if we go back to the home page, there is no longer a 'New Contact phone number
Sample' tab.

    >>> browser.open(portal_url)
    >>> 'New Contact phone number Sample' in browser.contents
    False

Adding a new Contact phone number content item as contributor
------------------------------------------------

Not only site managers are allowed to add Contact phone number content items, but
also site contributors.

Let's logout and then login as 'contributor', a portal member that has the
contributor role assigned.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url + '/login_form')
    >>> browser.getControl(name='__ac_name').value = 'contributor'
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

We select 'Contact phone number' and click the 'Add' button to get to the add form.

    >>> browser.getControl('Contact phone number').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'Contact phone number' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'Contact phone number Sample'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

Done! We added a new Contact phone number content item logged in as contributor.

Finally, let's login back as manager.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url + '/login_form')
    >>> browser.getControl(name='__ac_name').value = portal_owner
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)


The Contact email address content type
===============================

In this section we are tesing the Contact email address content type by performing
basic operations like adding, updadating and deleting Contact email address content
items.

Adding a new Contact email address content item
--------------------------------

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

Then we select the type of item we want to add. In this case we select
'Contact email address' and click the 'Add' button to get to the add form.

    >>> browser.getControl('Contact email address').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'Contact email address' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'Contact email address Sample'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

And we are done! We added a new 'Contact email address' content item to the portal.

Updating an existing Contact email address content item
---------------------------------------

Let's click on the 'edit' tab and update the object attribute values.

    >>> browser.getLink('Edit').click()
    >>> browser.getControl(name='title').value = 'New Contact email address Sample'
    >>> browser.getControl('Save').click()

We check that the changes were applied.

    >>> 'Changes saved' in browser.contents
    True
    >>> 'New Contact email address Sample' in browser.contents
    True

Removing a/an Contact email address content item
--------------------------------

If we go to the home page, we can see a tab with the 'New Contact email address
Sample' title in the global navigation tabs.

    >>> browser.open(portal_url)
    >>> 'New Contact email address Sample' in browser.contents
    True

Now we are going to delete the 'New Contact email address Sample' object. First we
go to the contents tab and select the 'New Contact email address Sample' for
deletion.

    >>> browser.getLink('Contents').click()
    >>> browser.getControl('New Contact email address Sample').click()

We click on the 'Delete' button.

    >>> browser.getControl('Delete').click()
    >>> 'Item(s) deleted' in browser.contents
    True

So, if we go back to the home page, there is no longer a 'New Contact email address
Sample' tab.

    >>> browser.open(portal_url)
    >>> 'New Contact email address Sample' in browser.contents
    False

Adding a new Contact email address content item as contributor
------------------------------------------------

Not only site managers are allowed to add Contact email address content items, but
also site contributors.

Let's logout and then login as 'contributor', a portal member that has the
contributor role assigned.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url + '/login_form')
    >>> browser.getControl(name='__ac_name').value = 'contributor'
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

We select 'Contact email address' and click the 'Add' button to get to the add form.

    >>> browser.getControl('Contact email address').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'Contact email address' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'Contact email address Sample'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

Done! We added a new Contact email address content item logged in as contributor.

Finally, let's login back as manager.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url + '/login_form')
    >>> browser.getControl(name='__ac_name').value = portal_owner
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)


The Contact net address content type
===============================

In this section we are tesing the Contact net address content type by performing
basic operations like adding, updadating and deleting Contact net address content
items.

Adding a new Contact net address content item
--------------------------------

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

Then we select the type of item we want to add. In this case we select
'Contact net address' and click the 'Add' button to get to the add form.

    >>> browser.getControl('Contact net address').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'Contact net address' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'Contact net address Sample'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

And we are done! We added a new 'Contact net address' content item to the portal.

Updating an existing Contact net address content item
---------------------------------------

Let's click on the 'edit' tab and update the object attribute values.

    >>> browser.getLink('Edit').click()
    >>> browser.getControl(name='title').value = 'New Contact net address Sample'
    >>> browser.getControl('Save').click()

We check that the changes were applied.

    >>> 'Changes saved' in browser.contents
    True
    >>> 'New Contact net address Sample' in browser.contents
    True

Removing a/an Contact net address content item
--------------------------------

If we go to the home page, we can see a tab with the 'New Contact net address
Sample' title in the global navigation tabs.

    >>> browser.open(portal_url)
    >>> 'New Contact net address Sample' in browser.contents
    True

Now we are going to delete the 'New Contact net address Sample' object. First we
go to the contents tab and select the 'New Contact net address Sample' for
deletion.

    >>> browser.getLink('Contents').click()
    >>> browser.getControl('New Contact net address Sample').click()

We click on the 'Delete' button.

    >>> browser.getControl('Delete').click()
    >>> 'Item(s) deleted' in browser.contents
    True

So, if we go back to the home page, there is no longer a 'New Contact net address
Sample' tab.

    >>> browser.open(portal_url)
    >>> 'New Contact net address Sample' in browser.contents
    False

Adding a new Contact net address content item as contributor
------------------------------------------------

Not only site managers are allowed to add Contact net address content items, but
also site contributors.

Let's logout and then login as 'contributor', a portal member that has the
contributor role assigned.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url + '/login_form')
    >>> browser.getControl(name='__ac_name').value = 'contributor'
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

We select 'Contact net address' and click the 'Add' button to get to the add form.

    >>> browser.getControl('Contact net address').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'Contact net address' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'Contact net address Sample'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

Done! We added a new Contact net address content item logged in as contributor.

Finally, let's login back as manager.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url + '/login_form')
    >>> browser.getControl(name='__ac_name').value = portal_owner
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)


The Contact content type
===============================

In this section we are tesing the Contact content type by performing
basic operations like adding, updadating and deleting Contact content
items.

Adding a new Contact content item
--------------------------------

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

Then we select the type of item we want to add. In this case we select
'Contact' and click the 'Add' button to get to the add form.

    >>> browser.getControl('Contact').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'Contact' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'Contact Sample'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

And we are done! We added a new 'Contact' content item to the portal.

Updating an existing Contact content item
---------------------------------------

Let's click on the 'edit' tab and update the object attribute values.

    >>> browser.getLink('Edit').click()
    >>> browser.getControl(name='title').value = 'New Contact Sample'
    >>> browser.getControl('Save').click()

We check that the changes were applied.

    >>> 'Changes saved' in browser.contents
    True
    >>> 'New Contact Sample' in browser.contents
    True

Removing a/an Contact content item
--------------------------------

If we go to the home page, we can see a tab with the 'New Contact
Sample' title in the global navigation tabs.

    >>> browser.open(portal_url)
    >>> 'New Contact Sample' in browser.contents
    True

Now we are going to delete the 'New Contact Sample' object. First we
go to the contents tab and select the 'New Contact Sample' for
deletion.

    >>> browser.getLink('Contents').click()
    >>> browser.getControl('New Contact Sample').click()

We click on the 'Delete' button.

    >>> browser.getControl('Delete').click()
    >>> 'Item(s) deleted' in browser.contents
    True

So, if we go back to the home page, there is no longer a 'New Contact
Sample' tab.

    >>> browser.open(portal_url)
    >>> 'New Contact Sample' in browser.contents
    False

Adding a new Contact content item as contributor
------------------------------------------------

Not only site managers are allowed to add Contact content items, but
also site contributors.

Let's logout and then login as 'contributor', a portal member that has the
contributor role assigned.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url + '/login_form')
    >>> browser.getControl(name='__ac_name').value = 'contributor'
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

We select 'Contact' and click the 'Add' button to get to the add form.

    >>> browser.getControl('Contact').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'Contact' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'Contact Sample'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

Done! We added a new Contact content item logged in as contributor.

Finally, let's login back as manager.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url + '/login_form')
    >>> browser.getControl(name='__ac_name').value = portal_owner
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)



