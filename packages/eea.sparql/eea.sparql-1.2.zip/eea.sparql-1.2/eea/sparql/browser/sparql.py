""" sparql
"""
import logging

from Products.Five import BrowserView
from Products.ZSPARQLMethod.Method import interpolate_query_html
from Products.ZSPARQLMethod.Method import map_arg_values
from Products.ZSPARQLMethod.Method import parse_arg_spec
from eea.sparql.converter.sparql2json import sparql2json
from Products.CMFCore.utils import getToolByName
from time import time
import json
import urllib2
import contextlib

logger = logging.getLogger('eea.sparql')

class Sparql(BrowserView):
    """Sparql view"""

    def test_query(self):
        """test query"""
        arg_spec = parse_arg_spec(self.context.arg_spec)
        missing, arg_values = map_arg_values(arg_spec, self.request.form)
        error = None

        if missing:
            # missing argument
            data = None
            dt = 0

        else:
            t0 = time()

            try:
                self.context.timeout = max(
                    getattr(self.context, 'timeout', 10), 10)
                data = self.context.execute(**arg_values)

            except Exception:
                import traceback
                error = traceback.format_exc()
                data = None

            dt = time() - t0

        options = {
            'query': interpolate_query_html(self.context.query, arg_values),
            'query_with_comments': interpolate_query_html(
                self.context.query_with_comments, arg_values),
            'data': data,
            'duration': dt,
            'arg_spec': arg_spec,
            'error': error,
        }
        return options

    def json(self):
        """json"""
        data = self.context.execute_query()
        return json.dumps(sparql2json(data))

    def sparql_download(self):
        """ Download sparql results in various formats
        """
        download_format = self.request['format']
        title = self.context.title
        results = ''
        if download_format in ['exhibit', 'html', 'tsv', 'csv']:
            try:
                data = self.context.execute_query()
                jsonData = sparql2json(data)
            except Exception:
                data = None
                jsonData = {'properties':{}, 'items':{}}

            result = u''

            if download_format == 'exhibit':
                self.request.response.setHeader(
                    'Content-Type', 'application/json')
                self.request.response.setHeader(
                    'Content-Disposition',
                        'attachment; filename="%s.json"' %title)
                result = json.dumps(jsonData)

            if download_format == 'html':
                result += u"<style type='text/css'>\r\n"
                result += u"table{border-collapse:collapse}\r\n"
                result += u"th,td {border:1px solid black}\r\n"
                result += u"</style>\r\n"
                result += u"<table>\r\n"
                result += u"\t<tr>\r\n"
                for col in jsonData['properties'].keys():
                    result += u"\t\t<th>" + col + u"</th>\r\n"
                result += u"\t</tr>\r\n"
                for row in jsonData['items']:
                    result += u"\t<tr>\r\n"
                    for col in jsonData['properties'].keys():
                        result += u"\t\t<td>" + unicode(row[col]) + "</td>\r\n"
                    result += u"\t</tr>\r\n"
                result += u"</table>\r\n"

            if download_format in ['csv', 'tsv']:
                self.request.response.setHeader(
                    'Content-Type', 'application/csv')
                self.request.response.setHeader(
                    'Content-Disposition',
                        'attachment; filename="%s.csv"' %title)
                separator = ', '
                if download_format == 'tsv':
                    self.request.response.setHeader(
                        'Content-Type', 'application/tsv')
                    self.request.response.setHeader(
                        'Content-Disposition',
                            'attachment; filename="%s.tsv"' %title)
                    separator = '\t'
                first = True
                for col in jsonData['properties'].keys():
                    if not first:
                        result += separator
                    result += col + ":" + jsonData[
                        'properties'][col]['valueType']
                    first = False

                result += u"\r\n"
                for row in jsonData['items']:
                    first = True
                    for col in jsonData['properties'].keys():
                        if not first:
                            result += separator
                        result += unicode(row[col])
                        first = False

                    result += u"\r\n"

            return result

        elif download_format in ['json', 'xml', 'xml_with_schema']:
            endpoint = self.context.endpoint_url
            query = 'query='+self.context.query
            headers = ''
            if download_format == 'json':
                headers = {'Accept' : 'application/sparql-results+json'}
                self.request.response.setHeader(
                    'Content-Type', 'application/json')
                self.request.response.setHeader(
                    'Content-Disposition',
                        'attachment; filename="%s.json"' %title)

            if download_format == 'xml':
                headers = {'Accept' : 'application/sparql-results+xml'}
                self.request.response.setHeader(
                    'Content-Type', 'application/xml')
                self.request.response.setHeader(
                    'Content-Disposition',
                        'attachment; filename="%s.xml"' %title)

            if download_format == 'xml_with_schema':
                headers = {'Accept' : 'application/x-ms-access-export+xml'}
                self.request.response.setHeader(
                    'Content-Type', 'application/xml')
                self.request.response.setHeader(
                    'Content-Disposition',
                        'attachment; filename="%s.xml"' %title)

            request = urllib2.Request(endpoint, query, headers)
            results = ""
            self.context.timeout = max(getattr(self.context, 'timeout', 10), 10)
            try:
                with contextlib.closing(urllib2.urlopen(
                    request, timeout = self.context.timeout)) as conn:
                    for data in conn:
                        self.request.response.write(data)
            except Exception:
                # timeout
                return results
            return results
        return results

class SparqlBookmarksFolder(Sparql):
    """SparqlBookmarksFolder view"""

    def getBookmarks(self):
        """Get list of bookmarks and check if needs to be updated"""
        results = self.test_query()
        queries = results['data']['rows']
        bookmarks = {}
        bookmarks['data'] = []
        bookmarks['arg_spec'] = results['arg_spec']
        bookmarks['error'] = results['error']
        bookmarks['duration'] = results['duration']
        query_endpoint = self.context.endpoint_url
        for query in queries:
            query_details = {}
            query_details['name'] = query[0].value
            query_details['sparql'] = query[2].value
            query_details['bookmark'] = query[1].value
            query_details['status'] = self.context.checkQuery(
                                        query_details['name'],
                                        query_endpoint,
                                        query_details['sparql'])
            bookmarks['data'].append(query_details)
        return bookmarks

    def addOrUpdateQuery(self):
        """Add or Update the Current Query"""
        ob = self.context.addOrUpdateQuery(self.request['title'],
                 self.context.endpoint_url,
                 self.request['query'])
        self.request.response.redirect(ob.absolute_url() + "/@@view")

    def syncQueries(self):
        """Synchronize all Queries"""
        self.context.syncQueries()
        self.request.response.redirect(self.context.absolute_url() + "/@@view")

class SparqlBookmarkFoldersSync(BrowserView):
    """ Sync all Bookmark Folders """

    def __call__(self):
        catalog = getToolByName(self, 'portal_catalog')
        brains = catalog.searchResults(portal_type = 'SparqlBookmarksFolder')
        for brain in brains:
            try:
                brain.getObject().syncQueries()
            except Exception, err:
                logger.exception(err)
        return "Sync done"
