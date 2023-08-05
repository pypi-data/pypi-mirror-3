raptus.multilanguageplone
=========================

Installation
------------

Login as Manager and try to install product raptus.multilanguageplone
To verify that nothing's wrong is happening

Login as manager
    >>> self.login()
    >>> self.setRoles(('Manager',))
    >>> from Products.CMFCore.utils import getToolByName
    
We set a multilingual site ('en' and 'fr'), with default lang = 'en', 
but using cookie negociation seems to be difficult in browser tests
so we force always_show_selector =1 and we use request negociation
    >>> langtool = getToolByName(self.portal, 'portal_languages')
    >>> langtool.manage_setLanguageSettings(supportedLanguages = ['en', 'fr'], defaultLanguage='fr') 
    >>> langtool.getSupportedLanguages()
    ['en', 'fr']
    >>> langtool.getDefaultLanguage()
    'fr'

Install raptus.multilanguageplone via quickinstaller
    >>> qi = getToolByName(self.portal, 'portal_quickinstaller')
    >>> _ = qi.installProducts(products=['raptus.multilanguageplone'])
    >>> qi.isProductInstalled('raptus.multilanguageplone')
    True

See if raptus.multilanguagefields is installed
    >>> qi.isProductInstalled('raptus.multilanguagefields')
    True
    
Create a multilingual document 
------------------------------    

Create a document with different values for each lang
    >>> self.portal.invokeFactory('Document', 'test-doc')
    'test-doc'
    >>> testdoc = getattr(self.portal, 'test-doc')

MultiLingual Fields are dicts using lang as key    
Edit multilingual title and text
    >>> multilingualtitle = {'fr' : 'Test doc fr', 'en' : 'Test doc en'}
    >>> multilingualtext = {'fr' : '<p>__FRENCH_CONTENT__</p>', 'en' : '<p>__ENGLISH_CONTENT__</p>'}
    >>> testdoc.edit( title = multilingualtitle, text= multilingualtext)

Publish test-doc
    >>> wf = getToolByName(self.portal, 'portal_workflow')
    >>> wf.doActionFor(testdoc, 'publish', comment='foo' )    

Get testdoc title, it must be french
    >>> testdoc.Title()
    'Test doc fr'

Get testdoc content, it must be french
    >>> '__FRENCH_CONTENT__' in testdoc.getText()
    True

Consultation tests in english
-----------------------------
It seems difficult to simulate a real language negociation in doctests
with the same user and without changing the portal default language
so ...
    >>> langtool.setDefaultLanguage('en')
    >>> self.portal.logout()    
    'http://nohost/logged_out'
    
Connect with default user, the accept-language HTTP ENV variable fixed to 'en'
The content response must be in english, and
must contain the english title and english content
    >>> from Products.PloneTestCase.setup import default_user, default_password
    >>> self.publish('%s/test-doc' %self.portal.absolute_url(1), 
    ...              '%s:%s' %(default_user,default_password), 
    ...              env={'HTTP_ACCEPT_LANGUAGE': 'en'})
    HTTPResponse(...
    ...lang="en"...
    ...Test doc en...
    ...__ENGLISH_CONTENT__...
    

Edition tests with testbrowser
------------------------------
It would be nice if we could test also lang negociation
with testbrowser but it seems complicated (see the problem below)
So we only test the multilingual edition form   

Set some variables for testbrowser connection
    >>> from Products.Five.testbrowser import Browser
    >>> browser = Browser()
    >>> portal_url = self.portal.absolute_url()
    >>> from Products.PloneTestCase.setup import portal_owner, default_password

I don't know why but testbrowser is broken with these classical
Plone connection lines on a multilingual plone site
If somebody can help me
"    >>> loginfield = browser.getControl(name=u'__ac_name')"
"    >>> loginfield.value = portal_owner"
"    >>> passfield = browser.getControl(name=u'__ac_password')"
"    >>> passfield.value = default_password"
"    >>> browser.getControl(name='submit').click()"


So connect as portal_owner using basic auth on zope instance
then on portal_url
    >>> browser.addHeader('Authorization', 'Basic portal_owner:portal_owner')
    >>> browser.addHeader('Accept-Language', 'en-us,en;q=0.7,fr;q=0.5')
    >>> browser.open(portal_url)
    
Create a multilingual News Item
-------------------------------

Create a News Item with different values for each lang
    >>> self.portal.invokeFactory('News Item', 'test-newsitem')
    'test-newsitem'
    >>> testnewsitem = getattr(self.portal, 'test-newsitem')

MultiLingual Fields are dicts using lang as key
Edit multilingual title and text
    >>> multilingualtitle = {'fr' : 'Test news item fr', 'en' : 'Test news item en'}
    >>> multilingualtext = {'fr' : '<p>__FRENCH_CONTENT__</p>', 'en' : '<p>__ENGLISH_CONTENT__</p>'}
    >>> testnewsitem.edit( title = multilingualtitle, text= multilingualtext)

Publish test-newsitem
    >>> wf = getToolByName(self.portal, 'portal_workflow')
    >>> wf.doActionFor(testnewsitem, 'publish', comment='foo' )

Get testnewsitem title, it must be french
    >>> testnewsitem.Title()
    'Test news item fr'

Get testnewsitem content, it must be french
    >>> '__FRENCH_CONTENT__' in testnewsitem.getText()
    True

Create a multilingual Image
---------------------------

Import dummy that has a dummy image for our tests

   >>> from Products.CMFPlone.tests import dummy

Create an Image with different values for each lang
    >>> self.portal.invokeFactory('Image', 'test-image', image=dummy.Image())
    'test-image'
    >>> testimage = getattr(self.portal, 'test-image')

MultiLingual Fields are dicts using lang as key
Edit multilingual title
    >>> multilingualtitle = {'fr' : 'Test image fr', 'en' : 'Test image en'}
    >>> testimage.edit( title = multilingualtitle)

Get testimage title, it must be french
    >>> testimage.Title()
    'Test image fr'

Create a multilingual File
--------------------------

Create a File with different values for each lang
    >>> self.portal.invokeFactory('File', 'test-file', file=dummy.File())
    'test-file'
    >>> testfile = getattr(self.portal, 'test-file')

MultiLingual Fields are dicts using lang as key
Edit multilingual title
    >>> multilingualtitle = {'fr' : 'Test file fr', 'en' : 'Test file en'}
    >>> testfile.edit( title = multilingualtitle)

Get testfile title, it must be french
    >>> testfile.Title()
    'Test file fr'

Create a multilingual Collection
--------------------------------

Create a Collection with different values for each lang
    >>> self.portal.invokeFactory('Topic', 'test-topic')
    'test-topic'
    >>> testtopic = getattr(self.portal, 'test-topic')

MultiLingual Fields are dicts using lang as key
Edit multilingual title
    >>> multilingualtitle = {'fr' : 'Test topic fr', 'en' : 'Test topic en'}
    >>> testtopic.edit( title = multilingualtitle)

Publish test-topic
    >>> wf = getToolByName(self.portal, 'portal_workflow')
    >>> wf.doActionFor(testtopic, 'publish', comment='foo' )

Get testtopic title, it must be french
    >>> testtopic.Title()
    'Test topic fr'

Create a multilingual Event
---------------------------

Create an Event with different values for each lang
    >>> self.portal.invokeFactory('Event', 'test-event')
    'test-event'
    >>> testevent = getattr(self.portal, 'test-event')

MultiLingual Fields are dicts using lang as key
Edit multilingual title and text
    >>> multilingualtitle = {'fr' : 'Test event fr', 'en' : 'Test event en'}
    >>> multilingualtext = {'fr' : '<p>__FRENCH_CONTENT__</p>', 'en' : '<p>__ENGLISH_CONTENT__</p>'}
    >>> testevent.edit( title = multilingualtitle, text= multilingualtext)

Publish test-event
    >>> wf = getToolByName(self.portal, 'portal_workflow')
    >>> wf.doActionFor(testevent, 'publish', comment='foo' )

Get testevent title, it must be french
    >>> testevent.Title()
    'Test event fr'

Get testevent content, it must be french
    >>> '__FRENCH_CONTENT__' in testevent.getText()
    True

Create a multilingual Folder
----------------------------

Create a Folder with different values for each lang
    >>> self.portal.invokeFactory('Folder', 'test-folder')
    'test-folder'
    >>> testfolder = getattr(self.portal, 'test-folder')

MultiLingual Fields are dicts using lang as key
Edit multilingual title
    >>> multilingualtitle = {'fr' : 'Test folder fr', 'en' : 'Test folder en'}
    >>> testfolder.edit( title = multilingualtitle)

Publish test-folder
    >>> wf = getToolByName(self.portal, 'portal_workflow')
    >>> wf.doActionFor(testfolder, 'publish', comment='foo' )

Get testfoldertitle, it must be french
    >>> testfolder.Title()
    'Test folder fr'

Create a multilingual Link
--------------------------

Create a Link with different values for each lang
    >>> self.portal.invokeFactory('Link', 'test-link')
    'test-link'
    >>> testlink = getattr(self.portal, 'test-link')

MultiLingual Fields are dicts using lang as key
Edit multilingual title and text
    >>> multilingualtitle = {'fr' : 'Test link fr', 'en' : 'Test link en'}
    >>> multilinguallink = {'fr' : 'http://www.plone.fr', 'en' : 'http://www.plone.com'}
    >>> testlink.edit( title = multilingualtitle, remote_url= multilinguallink)

Publish test-link
    >>> wf = getToolByName(self.portal, 'portal_workflow')
    >>> wf.doActionFor(testlink, 'publish', comment='foo' )

Get testlink title, it must be french
    >>> testlink.Title()
    'Test link fr'

Get testlink content, it must be french
    >>> testlink.getRemoteUrl()
    'http://www.plone.fr'


