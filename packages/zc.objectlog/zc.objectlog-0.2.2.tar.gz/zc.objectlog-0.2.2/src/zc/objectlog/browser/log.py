##############################################################################
#
# Copyright (c) 2005 Zope Corporation. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Visible Source
# License, Version 1.0 (ZVSL).  A copy of the ZVSL should accompany this
# distribution.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""views for logs

$Id: log.py 9509 2006-04-29 01:40:46Z gary $
"""
from zope import interface, component, i18n, proxy
from zope.app import zapi
from zope.interface.common.idatetime import ITZInfo
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.formlib import namedtemplate, form
import zope.publisher.browser

import zc.table.column
import zc.table.interfaces

from zc.objectlog import interfaces
import zc.objectlog.browser.interfaces
from zc.objectlog.i18n import _

class SortableColumn(zc.table.column.GetterColumn):
    interface.implements(zc.table.interfaces.ISortableColumn)

def dateFormatter(value, context, formatter):
    value = value.astimezone(ITZInfo(formatter.request))
    dateFormatter = formatter.request.locale.dates.getFormatter(
        'dateTime', length='medium')
    return dateFormatter.format(value)

def principalsGetter(context, formatter):
    principals = zapi.principals()
    return [principals.getPrincipal(pid) for pid in context.principal_ids]

def principalsFormatter(value, context, formatter): 
    return ', '.join([v.title for v in value])

def logFormatter(value, context, formatter):
    summary, details = value
    res = []
    if summary:
        res.append('<div class="logSummary">%s</div>' % (
            i18n.translate(summary,
                           context=formatter.request,
                           default=summary),))
    if details:
        res.append('<div class="details">%s</div>' % (
            i18n.translate(details,
                           context=formatter.request,
                           default=details),))
    if res:
        return '\n'.join(res)
    else:
        return i18n.translate(
            _('no_summary_or_details_available-log_view',
              '[no information available]'), context=formatter.request)

def changesGetter(item, formatter):
    obj = form.FormData(item.record_schema, item.record_changes)
    interface.directlyProvides(obj, item.record_schema)
    return obj

def recordGetter(item, formatter):
    obj = form.FormData(item.record_schema, item.record)
    interface.directlyProvides(obj, item.record_schema)
    return obj

def recordFormatter(value, item, formatter):
    view = component.getMultiAdapter(
        (value, item, formatter.request), name='logrecordview')
    view.update()
    return view.render()

default_template = namedtemplate.NamedTemplateImplementation(
    ViewPageTemplateFile('default.pt'),
    zc.objectlog.browser.interfaces.ILoggingView)

class LogView(zope.publisher.browser.BrowserPage):
    interface.implements(
        zc.objectlog.browser.interfaces.ILoggingView)
    component.adapts( # could move to IAdaptableToLogging ;-)
        interfaces.ILogging, IBrowserRequest)

    template = namedtemplate.NamedTemplate('default')

    columns = (
        SortableColumn(_('log_column-date', 'Date'),
                       lambda c, f: c.timestamp, dateFormatter),
        SortableColumn(_('log_column-principals', 'Principals'),
                       principalsGetter, principalsFormatter),
        zc.table.column.GetterColumn(
            _('log_column-log', 'Log'), lambda c, f: (c.summary, c.details),
            logFormatter),
        zc.table.column.GetterColumn(
            _('log_column-details', 'Changes'), changesGetter, recordFormatter),
    #    zc.table.column.GetterColumn(
    #        _('log_column-details', 'Full Status'), recordGetter, recordFormatter)
        )

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def update(self):
        formatter_factory = component.getUtility(
            zc.table.interfaces.IFormatterFactory)
        self.formatter = formatter_factory(
            self, self.request, interfaces.ILogging(self.context).log,
            columns=self.columns)

    def render(self):
        return self.template()

    def __call__(self):
        self.update()
        return self.render()

def objectGetter(item, formatter):
    return item.__parent__.__parent__

def objectFormatter(value, item, formatter):
    view = component.getMultiAdapter(
        (value, item, formatter), name='log source')
    view.update()
    return view.render()

class AggregatedLogView(LogView):
    interface.implements(
        zc.objectlog.browser.interfaces.IAggregatedLoggingView)
    component.adapts( # could move to IAdaptableToLogging ;-)
        interfaces.ILogging, IBrowserRequest)

    template = namedtemplate.NamedTemplate('default')

    columns = (
        SortableColumn(_('log_column-task', 'Source'),
                       objectGetter, objectFormatter),
        SortableColumn(_('log_column-date', 'Date'),
                       lambda c, f: c.timestamp, dateFormatter),
        SortableColumn(_('log_column-principals', 'Principals'),
                       principalsGetter, principalsFormatter),
        zc.table.column.GetterColumn(
            _('log_column-log', 'Log'), lambda c, f: (c.summary, c.details),
            logFormatter),
        zc.table.column.GetterColumn(
            _('log_column-details', 'Changes'),
            changesGetter, recordFormatter),
        )

    def update(self):
        formatter_factory = component.getUtility(
            zc.table.interfaces.IFormatterFactory)
        self.formatter = formatter_factory(
            self, self.request, interfaces.IAggregatedLog(self.context),
            columns=self.columns)
