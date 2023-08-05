from zope.interface import implements
from AccessControl import getSecurityManager, Unauthorized
from Products.CMFCore import permissions

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.portlet.similarcontent import SimilarContentPortletMessageFactory as _

from Products.ZCTextIndex.SetOps import mass_weightedIntersection, \
                                        mass_weightedUnion

from plone.memoize.instance import memoize

import math

class ISimilarContentPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    # TODO: Add any zope.schema fields here to capture portlet configuration
    # information. Alternatively, if there are no settings, leave this as an
    # empty interface - see also notes around the add form and edit form
    # below.

    num = schema.Int(title=_(u"Number of Results"),
                     description=_(u"Number of similar items to return"),
                     default=10,
                     required=True)

    ttc = schema.Int(title=_(u"Number of terms to consider"),
                     description=_(u"This is the number of terms we use to search for similar content. "
                                   "The more terms the more accurate, but slower"),
                     default=20,
                     required=True)

    cutoff = schema.Int(title=_(u"Cutoff for similarity (0-100)"),
                     description=_(u"Only return items whose similarity score is above this."),
                     default=22,
                     required=True)


    indexname = schema.TextLine(title=_(u"Index to use"),
                                description=_(u"This is the index we will use to find similar content"),
                                default=u"SearchableText",
                                required=True)

    types_to_search = schema.Tuple(title=_(u"Type to search"),
                                description=_(u"Define the types you want to show in the "
                                              "similar content portlet"),
                               required=True,
                               missing_value=tuple(),
                               value_type=schema.Choice(
                                   vocabulary="plone.app.vocabularies.ReallyUserFriendlyTypes"))



class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(ISimilarContentPortlet)

    # TODO: Set default values for the configurable parameters here
    types_to_search = []

    # TODO: Add keyword parameters for configurable parameters here
    # def __init__(self, some_field=u""):
    #    self.some_field = some_field

    def __init__(self, num=10, ttc=20, cutoff=22, indexname="SearchableText", types_to_search=None):
        self.num = num
        self.ttc = ttc
        self.cutoff = cutoff
        self.indexname = indexname
        self.types_to_search = types_to_search

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "Similar Content Portlet"


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('similarcontentportlet.pt')

    @property
    def available(self):
        return len(self.similar()) > 0

    @memoize
    def similar(self):
        zc = self.context.portal_catalog
        cat = zc._catalog
        idx = cat.indexes[self.data.indexname].index
        wordinfo = idx._wordinfo
        docweight = idx._docweight
        num = self.data.num
        ttc = self.data.ttc
        N = float(len(docweight))
        meandoclen = idx._totaldoclen() / N
        K1 = idx.K1
        B = idx.B
        K1_plus1 = K1 + 1.0
        B_from1 = 1.0 - B


        # Get the currrent object's path and rid (=docid)
        path = '/'.join(self.context.getPhysicalPath())
        rid = zc.getrid(path)
        
        if not rid:
            return []

        # Get all the words in the document
        wids = idx.get_words(rid)

        # Calculate the most 'important' words in this document and
        # we then use those as our query. More efficient than using
        # all words in the document.
        rwids = []
        Wd = docweight[rid]
        lenweight = B_from1 + B * Wd / meandoclen
        for wid in set(wids):
            d2f = wordinfo[wid]
            f = d2f[rid]
            tf = f * K1_plus1 / (f + K1 * lenweight)
            idf = math.log(1.0 + N / float(len(d2f))) 
            rwids.append((tf*idf, wid))

        # sort the wids by 'importance' and get the top 20
        rwids.sort()
        rwids.reverse()
        wids = [ wid for (wqt, wid) in rwids[:ttc] ]

        # Do the actual search. We use okapiindex._search_wids here 
        # to to the bulk of the work
        res = {}
        rget = res.get
        widres = idx._search_wids(wids)

        # union of all the results
        res = mass_weightedUnion(widres)

        # The max similarity score is the score we get matching ourself...
        maxscore = float(res[rid])
        # ...but we don't want to include ourself
        del res[rid]

        # Sort and un-decorate the document list
        res = [ (score,docid) for (docid,score) in res.items() ]
        res.sort()
        res.reverse()

        similar = []
        count = 0
        types_to_search = set(self.data.types_to_search)
        security_manager = getSecurityManager()

        for score, docid in res:
            normscore = int((score/maxscore)*100)
            if count > num or normscore < self.data.cutoff:
                break
            brain = cat[docid]
            try:
                if not security_manager.checkPermission(permissions.View, brain.getObject()):
                    continue
            except Unauthorized:
                continue
            if hasattr(self.context, 'Language') and hasattr(brain, 'Language'):
                if brain.Language!=self.context.Language():
                    continue
            if brain['portal_type'] in types_to_search:
                similar.append(brain)
                count += 1
        
        return similar


        


class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(ISimilarContentPortlet)

    def create(self, data):
        return Assignment(**data)


# NOTE: If this portlet does not have any configurable parameters, you
# can use the next AddForm implementation instead of the previous.

# class AddForm(base.NullAddForm):
#     """Portlet add form.
#     """
#     def create(self):
#         return Assignment()


# NOTE: If this portlet does not have any configurable parameters, you
# can remove the EditForm class definition and delete the editview
# attribute from the <plone:portlet /> registration in configure.zcml


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(ISimilarContentPortlet)
