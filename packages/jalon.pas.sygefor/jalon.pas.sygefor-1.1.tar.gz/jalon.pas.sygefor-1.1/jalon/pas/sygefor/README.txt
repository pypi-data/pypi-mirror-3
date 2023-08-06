Tests for jalon.pas.sygefor

test setup
----------

    >>> from Testing.ZopeTestCase import user_password
    >>> from Products.Five.testbrowser import Browser
    >>> browser = Browser()

Plugin setup
------------

    >>> acl_users_url = "%s/acl_users" % self.portal.absolute_url()
    >>> browser.addHeader('Authorization', 'Basic %s:%s' % ('portal_owner', user_password))
    >>> browser.open("%s/manage_main" % acl_users_url)
    >>> browser.url
    'http://nohost/plone/acl_users/manage_main'
    >>> form = browser.getForm(index=0)
    >>> select = form.getControl(name=':action')

jalon.pas.sygefor should be in the list of installable plugins:

    >>> 'Sygefor Helper' in select.displayOptions
    True

and we can select it:

    >>> select.getControl('Sygefor Helper').click()
    >>> select.displayValue
    ['Sygefor Helper']
    >>> select.value
    ['manage_addProduct/jalon.pas.sygefor/manage_add_sygefor_helper_form']

we add 'Sygefor Helper' to acl_users:

    >>> from jalon.pas.sygefor.plugin import SygeforHelper
    >>> myhelper = SygeforHelper('myplugin', 'Sygefor Helper')
    >>> self.portal.acl_users['myplugin'] = myhelper

and so on. Continue your tests here

    >>> 'ALL OK'
    'ALL OK'

