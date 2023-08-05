from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName


class ResponsibilitiesView(BrowserView):

    index = ViewPageTemplateFile('responsibilities.pt')

    def user(self):
        if 'user' in self.request:
            return self.request['user']
        mt = getToolByName(self.context, 'portal_membership')
        member_id = mt.getAuthenticatedMember().getId()
        return member_id

    def userVocabulary(self):
        mt = getToolByName(self.context, 'portal_membership')
        member_data = mt.listMembers()
        return dict(
            [(member.id, member.getProperty('fullname') or member.id, )
             for member in member_data
            ]
        )

    def responsibilities(self):
        ct = getToolByName(self.context, 'portal_catalog')
        member_id = self.user()
        if member_id is None:
            return []
        return ct.searchResults(responsibleperson = member_id)
