from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary
from Products.CMFCore.utils import getToolByName
from zope.interface import implements, implementer, alsoProvides
from zope.schema.interfaces import IVocabulary, IVocabularyFactory
from Products.ATSuccessStory import _

@implementer(IVocabulary)
def existingSSFolders( context ):
    pc = getToolByName(context, 'portal_catalog')
    pu = getToolByName(context, 'portal_url')
    portal = pu.getPortalObject()
    
    portal_path = '/'.join(portal.getPhysicalPath())
    
    results = pc.searchResults(portal_type='ATSuccessStoryFolder')
    
    terms = [SimpleVocabulary.createTerm(portal_path, portal_path, _(u'Global'))]

    for value in results:
        path = value.getPath()
        terms.append(SimpleVocabulary.createTerm(path, path, u'%s - %s'%(value.Title, value.getPath())))
    
    return SimpleVocabulary(terms)
    
alsoProvides(existingSSFolders, IVocabularyFactory)
