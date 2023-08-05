import re
import sys
import logging

from Acquisition import aq_base
from App.special_dtml import HTML
from DocumentTemplate.html_quote import html_quote
from DocumentTemplate.ustr import ustr
from OFS.SimpleItem import Item
from OFS.SimpleItem import logger
from OFS.SimpleItem import pretty_tb
from webdav.xmltools import escape as xml_escape

logger = logging.getLogger('Zope_Hotfix_CVE_2010_1104')

def _raise_standardErrorMessage(
    self, client=None, REQUEST={},
    error_type=None, error_value=None, tb=None,
    error_tb=None, error_message='',
    tagSearch=re.compile(r'[a-zA-Z]>').search,
    error_log_url=''):

    try:
        if error_type  is None: error_type =sys.exc_info()[0]
        if error_value is None: error_value=sys.exc_info()[1]

        # allow for a few different traceback options
        if tb is None and error_tb is None:
            tb=sys.exc_info()[2]
        if type(tb) is not type('') and (error_tb is None):
            error_tb = pretty_tb(error_type, error_value, tb)
        elif type(tb) is type('') and not error_tb:
            error_tb = tb

        # turn error_type into a string
        if hasattr(error_type, '__name__'):
            error_type=error_type.__name__

        if hasattr(self, '_v_eek'):
            # Stop if there is recursion.
            raise error_type, error_value, tb
        self._v_eek=1

        if str(error_type).lower() in ('redirect',):
            raise error_type, error_value, tb

        if not error_message:
            try:
                s = ustr(error_value)
            except:
                s = error_value
            try:
                match = tagSearch(s)
            except TypeError:
                match = None
            if match is not None:
                error_message=error_value

        if client is None: client=self
        if not REQUEST: REQUEST=self.aq_acquire('REQUEST')

        try:
            if hasattr(client, 'standard_error_message'):
                s=getattr(client, 'standard_error_message')
            else:
                client = client.aq_parent
                s=getattr(client, 'standard_error_message')
            kwargs = {'error_type': error_type,
                        'error_value': error_value,
                        'error_tb': error_tb,
                        'error_traceback': error_tb,
                        'error_message': xml_escape(str(error_message)),
                        'error_log_url': error_log_url}

            if getattr(aq_base(s),'isDocTemp',0):
                v = s(client, REQUEST, **kwargs)
            elif callable(s):
                v = s(**kwargs)
            else:
                v = HTML.__call__(s, client, REQUEST, **kwargs)
        except:
            logger.error(
                'Exception while rendering an error message',
                exc_info=True
                )
            try:
                strv = repr(error_value) # quotes tainted strings
            except:
                strv = ('<unprintable %s object>' %
                        str(type(error_value).__name__))
            v = strv + (
                (" (Also, the following error occurred while attempting "
                    "to render the standard error message, please see the "
                    "event log for full details: %s)")%(
                html_quote(sys.exc_info()[1]),
                ))
        raise error_type, v, tb
    finally:
        if hasattr(self, '_v_eek'): del self._v_eek
        tb=None

def initialize(context):
    Item.raise_standardErrorMessage = _raise_standardErrorMessage
    logger.info('Hotfix installed.')
