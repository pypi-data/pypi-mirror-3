Introduction
============

valentine.multiparagraphpage has got ideas from StructuredDocument, RichDocument and PloneArticle.

The goal is to have multiparagraphs and still make it as easy to edit and translate as normal page.

Lets create an object

  >>> self.setRoles(['Manager'])
  >>> mpage = self.portal[self.portal.invokeFactory('MultiParagraphPage', id='mpage1')]
  >>> paragraphs = ['<p>Simple paragraph1</p>', '<p>Simple paragraph2</p>', '<h2>Heading2</h2><p>Simple paragraph3</p>']

here we set the multiple paragraphs in a smart way ...

  >>> mpage.setText( paragraphs )
  >>> len(mpage.getText())
  3
  >>> for para in mpage.getText():
  ...   print para
  <p>Simple paragraph1</p>
  <p>Simple paragraph2</p>
  <h2>Heading2</h2><p>Simple paragraph3</p>


Changing order and removing paragraphs could be done just be resaving the list of paragraphs but maybe to expensive?
  >>> field = mpage.Schema()['text']
  >>> print mpage.getText()
  ('<p>Simple paragraph1</p>', '<p>Simple paragraph2</p>', '<h2>Heading2</h2><p>Simple paragraph3</p>')
  >>> field.moveDown(mpage, 0)
  >>> print mpage.getText()
  ('<p>Simple paragraph2</p>', '<p>Simple paragraph1</p>', '<h2>Heading2</h2><p>Simple paragraph3</p>')
  >>> field.moveUp(mpage, 1)
  >>> print mpage.getText()
  ('<p>Simple paragraph1</p>', '<p>Simple paragraph2</p>', '<h2>Heading2</h2><p>Simple paragraph3</p>')
  >>> mpage.reindexObject()


Searchable text should be contents from all paragraphs

  >>> mpage.SearchableText()
  'mpage1  <p>Simple paragraph1</p> <p>Simple paragraph2</p> <h2>Heading2</h2><p>Simple paragraph3</p>   '

  
Now we check the same content but contentportlets-aware
=======================================================

We manually add new portlet
  >>> from zope.component import getUtility, getMultiAdapter
  >>> from plone.portlets.interfaces import IPortletManager
  >>> portletManager = getUtility(IPortletManager, name=u'ContentPortlets')
  >>> from plone.portlet.static.static import Assignment as StaticPortlet
  >>> staticPortlet = StaticPortlet(header = 'MyHeader', text='portlet text', omit_border=True)
  >>> from plone.portlets.interfaces import IPortletAssignmentMapping
  >>> assignable = getMultiAdapter((mpage, portletManager), IPortletAssignmentMapping).__of__(mpage)
  >>> assignable['tempstatic'] = staticPortlet

Dedicated view returns the same data 
  >>> view = mpage.restrictedTraverse('@@multiparagraphpage_view')
  >>> view.getSlotsContent()
  ['<p>Simple paragraph1</p>', '<p>Simple paragraph2</p>', '<h2>Heading2</h2><p>Simple paragraph3</p>', u'<div class="portletStaticText portlet-static-myheader">portlet text</div>\n\n']
  
Manager will allow managing paragraphs without resaving the whole structure.
  >>> paragraphManager = mpage.restrictedTraverse('@@multiparagraphpage_view')
  >>> paragraphManager.removeParagraphOrPortlet(2) #index
  >>> view.getSlotsContent()
  ['<p>Simple paragraph1</p>', '<p>Simple paragraph2</p>', u'<div class="portletStaticText portlet-static-myheader">portlet text</div>\n\n']

Now we change the order  
  >>> paragraphManager.moveParagraphOrPortletUp(2)
  >>> view.getSlotsContent()
  ['<p>Simple paragraph1</p>', u'<div class="portletStaticText portlet-static-myheader">portlet text</div>\n\n', '<p>Simple paragraph2</p>']

Now we remove the portlet
  >>> paragraphManager.removeParagraphOrPortlet(1)
  >>> view.getSlotsContent()
  ['<p>Simple paragraph1</p>', '<p>Simple paragraph2</p>']
