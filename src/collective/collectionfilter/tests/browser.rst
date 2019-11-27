Integration tests
=================

    >>> browser = get_browser(layer)
    >>> portal = layer['portal']
    >>> memberName = 'siteManager'
    >>> portal.portal_membership.addMember(
    ...         memberName,
    ...         memberName,
    ...         ('Member', 'Manager',),
    ...         '',
    ...         {'fullname': 'Site Manager', 'email': memberName+'@dummy.fr',}
    ...         )

Log in with Site Manager access rights:

    >>> portal_url = portal.absolute_url()
    >>> browser.open(portal_url)
    >>> browser.getLink('Log in').click()
    >>> browser.getControl('Login Name').value = 'siteManager'
    >>> browser.getControl('Password').value = 'siteManager'
    >>> browser.getControl('Log in').click()


Add a collection search portlet:

    >>> portal_url = portal.absolute_url()
    >>> browser.open(portal_url +'/testcollection/++contextportlets++plone.rightcolumn/+/collective.collectionfilter.portlets.CollectionSearch')
    >>> browser.getControl(name='form.widgets.header').value = 'Search filter'
    >>> browser.getControl(name='form.widgets.button_text').value = 'Search button'
    >>> browser.getControl(name='form.widgets.placeholder').value = 'Search placeholder'
    >>> browser.getControl('Save').click()
    >>> browser.open(portal_url +'/testcollection')

    >>> input  =  browser.getForm(name='searchForm').getControl(name='SearchableText')
    >>> input.mech_control.attrs['placeholder']
    ... 'Search placeholder'
    >>> print browser.contents
    ...
    <button type="submit" ...>Search button</button>
    ...