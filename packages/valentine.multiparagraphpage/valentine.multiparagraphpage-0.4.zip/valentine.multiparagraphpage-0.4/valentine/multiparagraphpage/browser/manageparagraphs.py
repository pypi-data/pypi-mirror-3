from zope.interface import implements
from zope.component import getUtility, getMultiAdapter
from plone.app.kss.plonekssview import PloneKSSView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.portlets.interfaces import IPortletManager
from plone.app.portlets.browser.interfaces import IManageContentTypePortletsView
from plone.app.portlets.browser.manage import ManageContextualPortlets
from zope.annotation.interfaces import IAnnotations
from persistent.list import PersistentList
from plone.portlets.utils import unhashPortletInfo

STORAGE_KEY = 'multiparagragraphpage_slots'
#Workaround for removing portlets as I can't update the list of portlets within one request
REQUEST_KEY = 'multiparagragraphpage_removed_portlets' 

class ManagePortlets(ManageContextualPortlets):
    """
    I need to use adapter which is a child of ManageContextualPortlets to have proper context for inplace portlet editing.
    I mix two views on one page to handle all modifications. Maybe I could merge both classes but it works fine that way.
    """
    
    implements(IManageContentTypePortletsView)
    
    template = ViewPageTemplateFile('manageparagraphs.pt')
    
    def __init__(self, context, request):
        """
        Default view disables border so I override it
        """
        super(ManageContextualPortlets, self).__init__(context, request)

    def getParagraphsView(self):
        """
        Different view to handle local AJAX
        """
        
        return ManageParagraphs(self.context, self.request)

    def set_manageparagraphs_blacklist_status(self, manager, group_status, content_type_status, context_status):
        """
        Customized function to provide consistent content portlet management
        """
        ManageContextualPortlets.set_blacklist_status(self, manager, group_status, content_type_status, context_status)
        baseUrl = str(getMultiAdapter((self.context, self.request), name='absolute_url'))
        self.request.response.redirect(baseUrl + '/@@manageparagraphs')
        return ''

class ManageParagraphs(PloneKSSView):
    """
    AJAXified view to manage mixture of portlets and paragraphs
    """

    def __init__(self, context, request):
        """
        Default view disables border so I override it
        """
        super(PloneKSSView, self).__init__(context, request)
        self.contentPortlets = getMultiAdapter((self.context, self.request), name='contentportlets')
        annotations = IAnnotations(context)
        self.__mapping = annotations.get(STORAGE_KEY, None)
        if self.__mapping is None:
            self.__mapping = PersistentList()
            annotations[STORAGE_KEY] = self.__mapping
            if hasattr(context.aq_inner, '_paragraph_slots'):
                self.__mapping.extend(context._paragraph_slots)
                delattr(context.aq_inner, '_paragraph_slots')
        #That part is a workaround for removed portles to track them within request        
        requestAnnotations = IAnnotations(request)
        if requestAnnotations.get(REQUEST_KEY, None) is None:
            requestAnnotations[REQUEST_KEY] = []
        self.__removedPortlets = requestAnnotations[REQUEST_KEY]
        self.__portletNames = self.contentPortlets.getPortletNames()
    
   
    def getSlotsContent(self):
        """
        List of rendered slots
        """
        context = self.context
        paragraphs = context.getText()
        portlets = self.contentPortlets.getPortlets()
        self.updateSlots()
        slots = self.__mapping
        returnList = []
        for slot in slots:
            index = int(slot[3:])
            if slot.startswith('pa'):
                returnList.append(paragraphs[index])
            elif slot.startswith('po'):
                returnList.append(portlets[int(index)])
        return returnList        
            
    def getSlots(self):
        """
        List of slots
        """
        self.updateSlots()
        return self.__mapping
            
    def updateSlots(self):
        """
        I check current list of slots on each request. If paragraph or portlet is removed, local list is updated too.
        """
        context = self.context
        slots = self.__mapping
        removedPortlets = self.__removedPortlets
        portletNames = self.__portletNames
        paragraphs = context.getText()
        numberOfPortlets = len(self.__portletNames)
        numberOfFilteredPortlets = len([p for p in portletNames if p not in removedPortlets])
        numerOfParagraphs = len(paragraphs)
        if not len(slots):
            paragraphsList = ['pa_%d'%i for i in range(len(paragraphs))]
            portletsList = ['po_%d'%i for i in range(numberOfFilteredPortlets)]
            slots.extend(paragraphsList + portletsList)
            return True
        paragraphBools = [False]*(len(paragraphs))    
        portletBools = [False]*(numberOfPortlets)
        finalList = []
        for slot in slots:
            no = int(slot[3:])
            if slot.startswith('pa'):
                if no>= numerOfParagraphs or paragraphBools[no]:
                    continue
                paragraphBools[no] = True
            elif slot.startswith('po'):
                if no >= numberOfPortlets or portletBools[no]:
                    continue
                portletBools[no] = True
                if portletNames[no] in removedPortlets:
                    continue
            finalList.append(slot)
        for paEnum in enumerate(paragraphBools):
            if not paEnum[1]:
                finalList.append('pa_%d'%paEnum[0])
        for poEnum in enumerate(portletBools):
            if (not poEnum[1]) and (not portletNames[poEnum[0]] in removedPortlets):
                finalList.append('po_%d'%poEnum[0])
        if slots != finalList:
            IAnnotations(context)[STORAGE_KEY] = self.__mapping = PersistentList(finalList)
            return True
        return False
            
    
    def moveParagraphOrPortletUp(self, position, inplace=False):
        """
        """
        self.updateSlots()
        context = self.context
        slots = self.__mapping
        position = int(position)
        if position>0:
            slots[position], slots[position-1] = slots[position-1], slots[position]
        if inplace:
            return self.updateParagraphs()
        else:
            self.request.RESPONSE.redirect('%s/@@manageparagraphs'%self.context.absolute_url())
        
    def moveParagraphOrPortletDown(self, position, inplace=False):
        """
        """
        self.updateSlots()
        context = self.context
        slots = self.__mapping
        position = int(position)
        if position<len(slots)-1:
            slots[position], slots[position+1] = slots[position+1], slots[position]
        if inplace:
            return self.updateParagraphs()
        else:
            self.request.RESPONSE.redirect('%s/@@manageparagraphs'%self.context.absolute_url())
    
    def removeParagraphOrPortlet(self, position=None, portlethash = None, inplace=False):
        """
        """
        if portlethash:
            info = unhashPortletInfo(portlethash)
            self.__removedPortlets.append(info['name'])
        else:
            context = self.context
            slots = self.__mapping
            position = int(position)
            slot = slots[position]
            no = int(slot[3:])
            if slot.startswith('pa'):
                field = self.context.Schema()['text']
                field.remove(self.context, no)
            elif slot.startswith('po'):
                self.contentPortlets.removePortlet(no)
                self.__removedPortlets.append(self.__portletNames[no])
                self.updatePortlets()
            del slots[position]
        self.updateSlots()    
        if inplace:
            return self.updateParagraphs()
        else:
            self.request.RESPONSE.redirect('%s/@@manageparagraphs'%self.context.absolute_url())
    
    def addParagraph(self, position=None, inplace=False):
        """
        Not used now. I may use it if adding paragraphs will be required. I currently ignore position.
        """
        field = self.context.Schema()['text']
        field.add(self.context)
        if inplace:
            return self.updateParagraphs()
        else:
            self.request.RESPONSE.redirect('%s/@@manageparagraphs'%self.context.absolute_url())
    
            
    def updateParagraphs(self):
        """
        Updating macro
        """
        self.updateSlots()
        table = self.macroContent('@@manageparagraphs/template/macros/slots')
        ksscore = self.getCommandSet('core')
        selector = ksscore.getHtmlIdSelector('slots')
        ksscore.replaceInnerHTML(selector,table)
        return self.render()
    
    def updatePortlets(self):
        """
        Updating macro
        """
        table = self.macroContent('@@manageparagraphs/template/macros/portlets')
        ksscore = self.getCommandSet('core')
        selector = ksscore.getHtmlIdSelector('portlets')
        ksscore.replaceInnerHTML(selector,table)
        
    def getSlotParagraphs(self):
        """
        List of rendered slots
        """
        context = self.context
        paragraphs = context.getText()
        self.updateSlots()
        slots = self.__mapping
        returnList = []
        for slot in slots:
            index = int(slot[3:])
            if slot.startswith('pa'):
                returnList.append((index, paragraphs[index]))
        return returnList     
   

