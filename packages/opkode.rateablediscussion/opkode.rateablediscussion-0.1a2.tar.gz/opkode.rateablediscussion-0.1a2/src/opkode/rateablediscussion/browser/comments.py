from zope.app.component.hooks import getSite
from zope.interface.declarations import alsoProvides
from zope.annotation.interfaces import IAnnotations
from zope.annotation.interfaces import IAttributeAnnotatable
from plone.app.discussion.browser.comments import CommentsViewlet
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class RateableCommentsViewlet(CommentsViewlet):
    """ """
    index = ViewPageTemplateFile('comments.pt')

    def update(self):
        super(RateableCommentsViewlet, self).update()
        pm = getToolByName(getSite(), 'portal_membership')
        self.member = pm.getAuthenticatedMember()

    def portal(self):
        return getSite()

    def is_anonymous(self):
        pm = getToolByName(self.context, 'portal_membership')
        return pm.isAnonymousUser()

    def get_member_vote(self, object):
        """ """
        if not IAttributeAnnotatable.providedBy(object):
            alsoProvides(object, IAttributeAnnotatable)
        annotations = IAnnotations(object)
        voters = annotations.get('opkode.rateablediscussion.voters', {})
        return voters.get(self.member.getId(), None)

    def get_rating(self, object):
        """ """
        if not IAttributeAnnotatable.providedBy(object):
            alsoProvides(object, IAttributeAnnotatable)
        annotations = IAnnotations(object)
        return annotations.get('opkode.rateablediscussion.rating', 0)


def initial_rating(obj, event):
    """ Give the comment creator an inital vote of +1 for the comment.
    """
    s = getSite()
    if not IAttributeAnnotatable.providedBy(obj):
        alsoProvides(obj, IAttributeAnnotatable)
    annotations = IAnnotations(obj)
    pm = getToolByName(s, 'portal_membership')
    member = pm.getAuthenticatedMember()
    annotations['opkode.rateablediscussion.voters'] = {member.getId(): 'up'}
    annotations['opkode.rateablediscussion.rating'] = 1
