# -*- coding: us-ascii -*-
# _______________________________________________________________________________
#
#  Copyright (c) 2011 OpenStudy, All rights reserved.
# _______________________________________________________________________________
#                                                                                 
#  This program is free software; you can redistribute it and/or modify         
#  it under the terms of the GNU General Public License as published by         
#  the Free Software Foundation, version 2.                                     
#                                                                                 
#  This program is distributed in the hope that it will be useful,             
#  but WITHOUT ANY WARRANTY; without even the implied warranty of               
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               
#  GNU General Public License for more details.                                 
#                                                                                 
#  You should have received a copy of the GNU General Public License           
#  along with this program; if not, write to the Free Software                 
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   
# _______________________________________________________________________________

__author__ = 'Brent Lambert <brent@enpraxis.net>'
__version__   = '$Revision 0.0 $'[11:-2]


from zope.interface import Interface, implements
from zope.component import adapts, getUtility, getMultiAdapter
from zope.schema import Choice
from zope.schema.vocabulary import SimpleVocabulary
try:
    from five.formlib.formbase import EditForm
except ImportError:
    from Products.Five.formlib.formbase import EditForm
from plone.app.form.validators import null_validator
from plone.portlets.interfaces import IPortletManager, IPortletAssignmentMapping
from Products.openstudy import portlets
from zope.formlib.form import FormFields, action, applyChanges, haveInputWidgets
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFCore.interfaces._content import IFolderish
from Products.CMFCore.interfaces import IPropertiesTool
from Products.CMFPlone import PloneMessageFactory
from Products.openstudy import OpenstudyMessageFactory as _
from urllib2 import urlopen
try:
    from json import loads
except ImportError:
    from simplejson import loads


def groupsvocab(context):
    """ Generate group list dynamically from data provided by OpenStudy """
    groups = ['None']
    ptool = getUtility(IPropertiesTool)
    if ptool:
        url = ptool.openstudy_properties.getProperty('apiurl')
        urlobj = urlopen(url)
        if urlobj:
            json_data = urlobj.read()
            groupdata = loads(json_data)
            groups += [x['name'] for x in groupdata]
    return SimpleVocabulary.fromValues(groups)


class IStudyGroupsForm(Interface):
    """ Form for managing study groups. """

    studygroup = Choice(title=_(u'Study Group'),
                        description=_(u'The OpenStudy group to associate with.'),
                        required=True,
                        vocabulary='openstudy.groupsvocab')


class StudyGroupsFormAdapter(SchemaAdapterBase):
    """ Study group adapter """
    
    adapts(IFolderish)
    implements(IStudyGroupsForm)

    def __init__(self, context):
        super(StudyGroupsFormAdapter, self).__init__(context)
        rightcolumn = getUtility(IPortletManager, name=u'plone.rightcolumn', context=context)
        self.right = getMultiAdapter((context, rightcolumn), IPortletAssignmentMapping, context=context)

    def get_studygroup(self):
        """ Look for default study group ID in portlet """
        if 'open-study' in self.right:
            return self.right['open-study'].studyGroupId
        return 'None'

    def set_studygroup(self, group):
        """ If a portlet does not exist, create one and set it to group """
        if 'None' == group:
            if 'open-study' in self.right:
                # Delete the portlet
                del self.right['open-study']
        elif 'open-study' in self.right:
            # Change the study group
            self.right['open-study'].studyGroupId = group
        else:
            # Create Openstudy
            self.right['open-study'] = portlets.openstudy.Assignment(studyGroupId=group)

    studygroup = property(get_studygroup, set_studygroup)


class ManageStudyGroupsEditForm(EditForm):
    """ Manage study groups """

    form_fields = FormFields(IStudyGroupsForm)
    label = _(u'OpenStudy Study Groups')
    description = _(u'Associate content with a study group.')

    def __init__(self, context, request):
        super(ManageStudyGroupsEditForm, self).__init__(context, request)

    @action(_(u'label_update', default='Update'),
            condition=haveInputWidgets,
            name=u'update')
    def handle_update_action(self, action, data):
        """ Create a new study group. """
        if applyChanges(self.context, self.form_fields, data, self.adapters):
           self.status = _(u"Study group settings updated.")
        else:
            self.status = _(u"Study group settings unchanged.")
            
        url = getMultiAdapter((self.context, self.request), name='absolute_url')()
        self.request.response.redirect(url)

    
