# -*- coding: utf-8 -*-
#
# File: Cooptation.py
#
# Copyright (c) 2011 by Ecreall
# Generator: ArchGenXML Version 2.7
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """Vincent Fretin and Michael Launay <development@ecreall.com>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from zope.interface import implements
import interfaces

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.cooptation.config import *

##code-section module-header #fill in your manual code here
from archetypes.referencebrowserwidget.widget import ReferenceBrowserWidget
##/code-section module-header

copied_fields = {}
copied_fields['title'] = BaseSchema['title'].copy()
copied_fields['title'].required = 1
copied_fields['title'].widget.label = "Full Name"
copied_fields['title'].widget.label_msgid = "label_full_name"
copied_fields['title'].widget.description = "Enter full name, eg. John Smith."
copied_fields['title'].widget.description_msgid = "help_full_name_creation"
copied_fields['title'].widget.i18n_domain = "plone"
schema = Schema((

    copied_fields['title'],

    StringField(
        name='username',
        widget=StringField._properties['widget'](
            label="User Name",
            label_msgid="label_user_name",
            description="Enter a user name.",
            description_msgid="help_user_name_creation_casesensitive",
            i18n_domain="plone",
        ),
        write_permission="Review portal content",
    ),
    StringField(
        name='email',
        widget=StringField._properties['widget'](
            label="E-mail",
            label_msgid="label_email",
            description="Enter an email address.",
            description_msgid="help_email_creation",
            i18n_domain="plone",
        ),
        required=1,
    ),
    TextField(
        name='reason',
        widget=TextAreaWidget(
            label="Reason",
            label_msgid="label_reason",
            description="Enter the reason of this inscription.",
            description_msgid="help_reason",
            i18n_domain='cooptation',
        ),
    ),
    ReferenceField(
        name='workspace',
        widget=ReferenceBrowserWidget(
            visible=-1,
            label='Workspace',
            label_msgid='cooptation_label_workspace',
            i18n_domain='cooptation',
        ),
        relationship="workspace",
    ),
    StringField(
        name='role',
        widget=SelectionWidget(
            label="Role",
            visible=-1,
            label_msgid='cooptation_label_role',
            i18n_domain='cooptation',
        ),
        vocabulary=['Reviewer', 'Editor', 'Reader'],
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

Cooptation_schema = BaseSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class Cooptation(BaseContent, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()
    implements(interfaces.ICooptation)

    meta_type = 'Cooptation'
    _at_rename_after_creation = True

    schema = Cooptation_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods


registerType(Cooptation, PROJECTNAME)
# end of class Cooptation

##code-section module-footer #fill in your manual code here
##/code-section module-footer

