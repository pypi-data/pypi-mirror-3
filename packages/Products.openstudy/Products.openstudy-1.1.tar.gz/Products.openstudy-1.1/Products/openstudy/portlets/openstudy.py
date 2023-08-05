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


from zope.interface import implements
from zope.formlib import form
from zope import schema
from zope.component import getMultiAdapter
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.app.portlets.portlets import base
from Products.openstudy import OpenstudyMessageFactory as _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from urllib import quote


class IOpenStudyPortlet(IPortletDataProvider):
    """ A portlet for OpenStudy integration """

    studyGroupId = schema.TextLine(
        title = _(u'label_studygroup_id', default=u'Study Group ID'),
        description = _(u'help_studygroup_id', 
                        default=u'The id of the study group to associate with.'),
        default = u'',
        required = True)
    

class Assignment(base.Assignment):
    """ Assignment Class """

    implements(IOpenStudyPortlet)

    @property
    def title(self):
        return _(u'Open Study Portlet')

    def __init__(self, studyGroupId=''):
        self.studyGroupId = studyGroupId    


class Renderer(base.Renderer):
    """ Renderer Class """

    render = ViewPageTemplateFile('openstudyportlet.pt')

    def getStudyGroup(self):
        return quote(self.data.studyGroupId)


class AddForm(base.AddForm):
    """ Add a study group. """
    
    form_fields = form.Fields(IOpenStudyPortlet)
    label = _(u'Add Study Group')
    description = _(u'Add a study group portlet from the OpenStudy project.')

    def create(self, data):
        return Assignment(studyGroupId=data.get('studyGroupId', u''))


class EditForm(base.EditForm):
    """ Edit an existing study group. """

    form_fields = form.Fields(IOpenStudyPortlet)
    label = _(u'Edit Study Group')
    description = _(u'Edit study group portlet settings.')

