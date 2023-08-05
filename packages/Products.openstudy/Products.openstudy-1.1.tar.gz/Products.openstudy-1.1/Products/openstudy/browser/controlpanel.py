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
from zope.schema import TextLine
from zope.formlib.form import FormFields
from zope.component import adapts, getUtility
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFCore.interfaces import IPropertiesTool
from plone.app.controlpanel.form import ControlPanelForm
from Products.openstudy import OpenstudyMessageFactory as _


class IOpenStudyControlPanelSchema(Interface):
    """ Schema for Openstudy Control Panel """

    apiurl = TextLine(title=_(u'label_openstudy_apiurl', default=u'API URL'),
                      description=_(u'label_help_openstudy_apiurl',
                                    default=u'URL for the OpenStudy API'),
                      required=True)


class OpenStudyControlPanelAdapter(SchemaAdapterBase):
    """ OpenStudy control panel adapter """
    
    adapts(IPloneSiteRoot)
    implements(IOpenStudyControlPanelSchema)

    def __init__(self, context):
        super(OpenStudyControlPanelAdapter, self).__init__(context)
        props = getUtility(IPropertiesTool)
        self.osprops = props.openstudy_properties

    def get_apiurl(self):
        return self.osprops.getProperty('apiurl')

    def set_apiurl(self, url):
        self.osprpos.manage_changeProperties(apiurl=url)

    apiurl = property(get_apiurl, set_apiurl)


class OpenStudyControlPanel(ControlPanelForm):
    """ OpenStudy control panel """

    form_fields = FormFields(IOpenStudyControlPanelSchema)
    label = _(u'OpenStudy Settings')
    description =_(u'Get and set options for configuring OpenStudy study groups.')
    form_name = _(u'OpenStudy Settings')

