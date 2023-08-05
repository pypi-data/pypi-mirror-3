from Products.Five import BrowserView
from zope.component import getUtility, getMultiAdapter
from Products.CMFPlone.interfaces import IPloneSiteRoot

class Migrator(BrowserView):
    """
    """

    def migrate(self):
        """
        I'm using inplace migrator from contentmigration product. 
        I made some tests with simple __class__ replacing but I decided that dedicated product will be safer to use.
        """
        from Products.contentmigration.archetypes import InplaceATItemMigrator
        from Products.StructuredDocument.contents.chapter import SimpleChapter
        portal = getUtility(IPloneSiteRoot)
        count = 0
        for chapter in portal.portal_catalog(portal_type='SimpleChapter', Language='all'):
            path = chapter.getPath()
            obj = chapter.getObject()
            modificationDate = obj.ModificationDate()
            data = [p.getObject().getText() for p in obj.objectValues() if p.portal_type=='SimpleParagraph']
            mp_migrator = InplaceATItemMigrator(obj)
            mp_migrator.dst_portal_type = 'MultiParagraphPage'
            mp_migrator.dst_meta_type = 'MultiParagraphPage'
            mp_migrator.migrate()
            newObj = portal.restrictedTraverse(path)
            newObj.setText(data)
            newObj.setModificationDate(modificationDate)
            newObj.reindexObject()
        
        for chapter in portal.portal_catalog(portal_type='Document', Language='all'):
                path = chapter.getPath()
                obj = chapter.getObject()
                modificationDate = obj.ModificationDate()
                data = obj.getText()
                mp_migrator = InplaceATItemMigrator(obj)
                mp_migrator.dst_portal_type = 'MultiParagraphPage'
                mp_migrator.dst_meta_type = 'MultiParagraphPage'
                mp_migrator.migrate()
                newObj = portal.restrictedTraverse(path)
                newObj.setText([data])
                newObj.setModificationDate(modificationDate)
                newObj.reindexObject()
                count += 1
                print newObj.absolute_url()

                
            
        return "Data migrated %d" % count
    
    
