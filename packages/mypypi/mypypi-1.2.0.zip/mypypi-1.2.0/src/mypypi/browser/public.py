##############################################################################
#
# Copyright (c) 2009 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id: public.py 2991 2012-07-01 22:49:52Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import re

import zope.interface
import zope.component
import zope.event
import zope.lifecycleevent
import zope.schema
import zope.security
from zope.traversing.browser import absoluteURL
from zope.publisher.browser import BrowserPage

import z3c.tabular.table
from z3c.template.template import getPageTemplate
from z3c.template.template import getLayoutTemplate
from z3c.form import field
from z3c.form import button
from z3c.formui import form
from z3c.table import column

import p01.fsfile.schema
import p01.fsfile.browser
import p01.fsfile.interfaces
import p01.tmp.interfaces

from mypypi.i18n import MessageFactory as _
from mypypi import interfaces
from mypypi import public
from mypypi.browser.setuptools import errorResponse


class PublicFiles(z3c.tabular.table.DeleteFormTable):
    """Public file management page."""

    zope.interface.implements(interfaces.IPublicFileManagementPage)

    buttons = z3c.tabular.table.DeleteFormTable.buttons.copy()
    handlers = z3c.tabular.table.DeleteFormTable.handlers.copy()

    formErrorsMessage = _('There were some errors.')
    ignoreContext = True
    errors  = []

    batchSize = 500
    startBatchingAt = 500

    simpleLayout = getLayoutTemplate('simple')
    simpleTemplate = getPageTemplate(name='simple')

    def __init__(self, context, request):
        if request.get('HTTP_USER_AGENT', '').lower().startswith('python-'):
            self.layout = self.simpleLayout
            self.template = self.simpleTemplate

        super(PublicFiles, self).__init__(context, request)

    def setUpColumns(self):
        return [
            column.addColumn(self, column.CheckBoxColumn, u'checkbox',
                             weight=1, cssClasses={'th':'firstColumnHeader'}),
            column.addColumn(self, column.LinkColumn, u'__name__',
                             weight=3),
            column.addColumn(self, column.CreatedColumn, name=u'created',
                             weight=4, header=u'Created'),
            column.addColumn(self, column.ModifiedColumn, name=u'modified',
                             weight=5, header=u'Modified')
            ]

    def setupConditions(self):
        interaction = zope.security.management.getInteraction()
        self.allowDelete = interaction.checkPermission('mypypi.ManagePublics',
                                           self.context)

        super(PublicFiles, self).setupConditions()

    @property
    def label(self):
        return _('Public File Management for $publicName',
            mapping={'publicName': self.context.__name__})

    def executeDelete(self, item):
        del self.context[item.__name__]

    def getCreatedDate(self, item):
        dc = IZopeDublinCore(item, None)
        v = dc.created
        if v is not None:
            return v.isoformat()
        return ''

    @property
    def links(self):
        baseURL = absoluteURL(self.context, self.request)
        return [{'name':name,
                  'url': '%s/%s' % (baseURL, name),
                  #'date': self.getCreatedDate(fle),
                  }
                for name, fle in self.context.items()]


class IPublicFileUploadSchema(interfaces.IPublicFile):
    """Public file upload schema."""

    upload = p01.fsfile.schema.FSFileUpload(
        title=_(u'Public File'),
        description=_(u'Public File'),
        fsStorageName=u'',
        fsNameSpace=u'upload', # use upload storage
        fsFileFactory=public.PublicFile,
        allowEmptyPostfix=False,
        required=True)


class PublicFileAddForm(form.AddForm):

    template = getPageTemplate(name='simple')

    buttons = form.AddForm.buttons.copy()
    handlers = form.AddForm.handlers.copy()

    label = _('Add Public File')

    fields = field.Fields(IPublicFileUploadSchema).select('__name__',
        'upload')

    def createAndAdd(self, data):
        try:
            # create
            name = data['__name__']
            publicFile = data['upload']

            # notify
            zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(
                publicFile))

            # add the release file
            self.context[name] = publicFile

            self._finishedAdd = True
            return publicFile

        except DuplicationError, e:
            self.status = _('Public file with the same name already exists.')
            return

    @button.buttonAndHandler(u'Cancel')
    def handleCancel(self, action):
        self.request.response.redirect(self.request.getURL())

    def nextURL(self):
        return '%s/index.html' % absoluteURL(self.context, self.request)


class PublicFileDownload(p01.fsfile.browser.FSFileDownload):
    """Public file download."""

    def __call__(self):
        return super(PublicFileDownload, self).__call__()


class PublicFileEditForm(form.EditForm):

    template = getPageTemplate(name='simple')

    label = _('Edit Public File')
