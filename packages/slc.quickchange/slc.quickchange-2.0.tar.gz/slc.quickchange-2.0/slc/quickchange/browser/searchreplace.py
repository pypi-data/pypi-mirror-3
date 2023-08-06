# -*- coding: utf-8 -*-
import re
import Acquisition
import StringIO
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_base, aq_parent, aq_inner
import os
from types import UnicodeType, StringType
from Products.Archetypes.public import RichWidget
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class SearchReplaceView(BrowserView):
    """ Doing Search and Replace on the current context """

    template = ViewPageTemplateFile('searchreplace.pt')

    def getName(self):
        return self.__name__

    def __init__(self, context, request):
        super(SearchReplaceView, self).__init__(context, request)
        self.request = request
        self.context = context
        self.changed = []
        self.search_text = None
        self.replace_text = None
        self.recursive = False
        self.regexp = False
        self.search_only = True
        self.path = None

    def __call__(self):
        self.request.set('disable_border', True)
        self.search_text = self.request.get('search_text', '')
        self.replace_text = self.request.get('replace_text', '')
        self.recursive = self.request.get('recursive', '')
        self.regexp = self.request.get('regexp', '')
        self.re_I = self.request.get('re_I', '')
        self.re_S = self.request.get('re_S', '')
        self.search_only = not self.request.get('form.button.Replace', False)
        self.alllangs = not not self.request.get('alllangs', None)

        self.path = "/".join(self.context.getPhysicalPath())

        self.do_replace()

        if len(self.changed):
            if self.search_only:
                message = u"The following objects would be found by your "
                "query (see below)"
            else:
                message = u"The following objects were fixed according to "
                "your query (see below)"
            plone_utils = getToolByName(self.context, 'plone_utils')
            plone_utils.addPortalMessage(message)
        return self.template()

    def do_replace(self):
        """ starting in the root, working through all language paths """
        if not self.search_text:
            return
        context = Acquisition.aq_inner(self.context)
        portal_languages = getToolByName(context, 'portal_languages')
        langs = portal_languages.getSupportedLanguages()
        portal_url = getToolByName(context, 'portal_url')
        portal = portal_url.getPortalObject()
        portal_catalog = getToolByName(context, 'portal_catalog')
        if hasattr(portal_catalog, 'getZCatalog'):
            portal_catalog = portal_catalog.getZCatalog()
        portal_path = "/".join(portal.getPhysicalPath())
        out = StringIO.StringIO()

        SR = SearchReplace()

        query = dict()
        queries = []
        # Recursive means: do a catalog query, based on paths
        # If translations of the elements up to the current level have
        # different ids, they won't be found this way.
        if self.recursive:
            if self.alllangs:
                # locate the language component in the path, if we have one.
                # If there is one, it is exactly below the portal path
                pathelems = self.path.split("/")
                langidx = len(portal.getPhysicalPath())
                if len(pathelems) >= langidx and len(pathelems[langidx]) == 2 \
                    and pathelems[langidx] in langs:
                    # we have a language branch
                    relpathelems = pathelems[langidx + 1:]
                    langpaths = []
                    for lang in langs:
                        langpath = "%(portal)s/%(lang)s/%(elems)s" % dict(
                            portal=portal_path, lang=lang,
                            elems="/".join(relpathelems))
                        langpaths.append(langpath)
                    query['path'] = langpaths
                    query['Language'] = 'all'
                else:
                    # no language branch, use the current path
                    query['path'] = self.path
            else:
                query['path'] = self.path
            results = portal_catalog(query)
        else:
            # A non-recursive search for all language version uses
            # LinguaPlone's getTranslation.
            # Here we are independent of paths / ids.
            if self.alllangs:
                results = list()
                for lang in langs:
                    trans = context.getTranslation(lang)
                    if trans:
                        results.append(trans)
            else:
                results = [context]

        params = dict(search=self.search_text,
            replace=self.replace_text,
            regexp=self.regexp,
            re_I=self.re_I,
            re_S=self.re_S,
            search_only=self.search_only)
        self.changed = []

        for result in results:
            if hasattr(Acquisition.aq_base(result), 'getObject'):
                try:
                    ob = result.getObject()
                except AttributeError, ae:
                    print "Error retrieving Object for %s" % result.getPath()
                    continue
            else:
                ob = result

            state = False

            changed = SR.apply(ob, params)
            state = state or changed

            if state:
                obpath = "/".join(ob.getPhysicalPath())
                oburl = ob.absolute_url()
                self.changed.append(oburl)


def _getRichTextFields(object):
    return [f for f in object.Schema().fields()
              if isinstance(f.widget, RichWidget)]


class SearchReplace:
    """ The Search & Replace Transforms can search for a given string and
    replace it by another string.
    The matching can bei either literal or use regular expressions.
    """

    def apply(self, object, params={}):
        """ apply a Search & Replace on the content of an object """
        state = False
        # Describes if a pattern has been found in this object.
        # If it has been found it'll also be replaced, so we can use this for
        # both search and replace mode.
        srch = params.get('search')
        rep = params.get('replace')
        search_only = params.get('search_only')
        ob = aq_base(object)
        regexp = params.get('regexp', 0)

        if type(srch) != UnicodeType:
            srch = unicode(srch, 'utf-8')
        if type(rep) != UnicodeType:
            rep = unicode(rep, 'utf-8')

        def sr_std(text):
            """ standard search replace using the string module """
            found = 0

            if type(text) != UnicodeType:
                try:
                    text = unicode(text, 'utf-8')
                except:
                    try:
                        text = unicode(text, 'iso8859-15')
                    except:
                        # Log error?
                        return(text, False)
            if text.find(srch) != -1:
                found = 1

            if search_only:
                ntext = text
            else:
                ntext = text.replace(srch, rep)

            return ntext.encode('utf-8'), found

        def sr_regexp(text):
            """ search and replace using regexp module """
            found = 0
            if type(text) != UnicodeType:
                try:
                    text = unicode(text, 'utf-8')
                except:
                    try:
                        text = unicode(text, 'iso8859-15')
                    except:
                        # Log error?
                        return(text, False)
            flags = None
            if params.get('re_I', ''):
                flags = re.I
            if params.get('re_S', ''):
                if flags:
                    flags = flags | re.S
                else:
                    flags = re.S
            if flags:
                patt = re.compile(srch, flags)
            else:
                patt = re.compile(srch)
            if re.findall(patt, text):
                found = 1

            if search_only:
                ntext = text
            else:
                ntext = re.sub(patt, rep, text)
            return ntext.encode('utf-8'), found

        method = sr_std
        if regexp:
            method = sr_regexp

        if ob.portal_type in ['Document', 'RichDocument', 'News Item',
            'Event', 'Topic', 'PressRoom', 'PressRelease', 'PressClip',
            'PressContact']:
            ntext = ntitle = ndescription = ''
            fields = _getRichTextFields(object)
            state = False

            for field in fields:
                text = field.getRaw(object)
                ntext, changed = method(text)
                state = state or changed
                if changed:
                    field.set(object, ntext)

            title = object.Title()
            ntitle, changed = method(title)
            state = state or changed
            if changed:
                object.setTitle(ntitle)

            description = object.Description()
            ndescription, changed = method(description)
            state = state or changed
            if changed:
                object.setDescription(ndescription)

            return state

        if ob.portal_type in ['Folder', 'Large Plone Folder']:
            state = False
            ntitle = ndescription = ''

            title = object.Title()
            ntitle, changed = method(title)
            state = state or changed
            if changed:
                object.setTitle(ntitle)

            description = object.Description()
            ndescription, changed = method(description)
            state = state or changed
            if changed:
                object.setDescription(ndescription)

            return state

        elif ob.portal_type in ['File']:
            state = False
            ntitle = ndescription = ''
            ndata = ''

            title = object.Title()
            ntitle, changed = method(title)
            state = state or changed
            if changed:
                object.setTitle(ntitle)

            description = object.Description()
            ndescription, changed = method(description)
            state = state or changed
            if changed:
                object.setDescription(ndescription)

            if object.getContentType().startswith('text/'):
                data = str(object.getFile().data)
                ndata, changed = method(data)
                state = state or changed
                if changed:
                    object.setFile(ndata)

            return state
