from plone.app.layout.viewlets.comments import CommentsViewlet as BaseCommentsViewlet
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class CommentsViewlet(BaseCommentsViewlet):
    """ New viewlet based on original comments viewlet. """

    index = ViewPageTemplateFile('comments.pt')
