from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.workflow.browser.sharing import SharingView as SharingViewOrig
from plone.app.workflow.browser.kss_sharing import KSSSharingView as KSSSharingViewOrig


class SharingView(SharingViewOrig):

    template = ViewPageTemplateFile('sharing.pt')
    oddclass = 'odd'
    evenclass = 'even'


class KSSSharingView(KSSSharingViewOrig):

    template = ViewPageTemplateFile('sharing.pt')


class DeployGroupMembers(SharingViewOrig):

    template = ViewPageTemplateFile('sharing.pt')
    macro_wrapper = ViewPageTemplateFile('deploygroup_macro_wrapper.pt')

    def __call__(self):
        sharing = getMultiAdapter((self.context, self.request), name="sharing")
        sharing.indent = True
        if self.request.get('oddrow', None) == 'even':
            sharing.oddclass, sharing.evenclass = 'even', 'odd'
        else:
            sharing.oddclass, sharing.evenclass = 'odd', 'even'

        the_id = 'user-group-sharing-settings'
        macro = self.template.macros[the_id]
        res = self.macro_wrapper(the_macro=macro, instance=self.context,
                view=sharing,
                role_settings=self.role_settings,
                available_roles=self.roles)
        self.request.RESPONSE.setHeader('Cache-Control', 'no-cache')
        self.request.RESPONSE.setHeader('Pragma', 'no-cache')
        return res

    def role_settings(self):
        """Get principals of the group.

        Returns a list of dicts with keys:

         - id
         - title
         - type (one of 'group' or 'user')
         - roles

        'roles' is a dict of settings, with keys of role ids as returned by
        roles(), and values True if the role is explicitly set, False
        if the role is explicitly disabled and None if the role is inherited.
        """
        mtool = getToolByName(self.context, "portal_membership")
        gtool = getToolByName(self.context, "portal_groups")
        getMemberById = mtool.getMemberById
        getGroupById = gtool.getGroupById
        isGroup = gtool.isGroup
        groupname = self.request['groupname']
        groupmembers = [getMemberById(m) or getGroupById(m)
                            for m in gtool.getGroupMembers(groupname)]
        groupmembers = [m for m in groupmembers if m]

        existing_principals = set([p['id'] for p in self.existing_role_settings()])
        empty_roles = dict([(r['id'], False) for r in self.roles()])
        info = []

        for principal in groupmembers:
            principal_id = principal.getId()
            if principal_id not in existing_principals:
                roles = empty_roles.copy()

                for r in principal.getRoles():
                    if r in roles:
                        roles[r] = 'global'

                info.append(dict(id = principal_id,
                                 title = principal.getProperty('fullname',
                                     principal.getProperty('title')
                                     ),
                                 type = isGroup(principal) and 'group' or 'user',
                                 roles = roles))

        info.sort(key=lambda x: safe_unicode(x["type"])+safe_unicode(x["title"]))
        return info
