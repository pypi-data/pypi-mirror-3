"""Definition of the Sparql content type
"""

from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata, base
from Products.ATContentTypes.content.folder import ATFolder

from Products.Archetypes import atapi
from Products.Archetypes.atapi import IntegerField, IntegerWidget
from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import StringField, StringWidget
from Products.Archetypes.atapi import TextField, TextAreaWidget
from Products.ZSPARQLMethod.Method import ZSPARQLMethod
from Products.ZSPARQLMethod.Method import parse_arg_spec, map_arg_values
from eea.cache import cache
from eea.sparql.config import PROJECTNAME
from eea.sparql.interfaces import ISparql, ISparqlBookmarksFolder
from eea.versions.interfaces import IVersionEnhanced
from eea.versions import versions

from zope.interface import implements

SparqlBaseSchema = atapi.Schema((
    StringField(
        name='endpoint_url',
        widget=StringWidget(
            label="Sparql endpoint URL",
        ),
        required=1
    ),
    IntegerField(
        name='timeout',
        widget=IntegerWidget(
            label="Timeout",
        ),
        required=0
    ),
    StringField(
        name='arg_spec',
        widget=StringWidget(
            label="Arguments",
        ),
        required=0
    ),
    TextField(
        name='sparql_query',
        default_content_type = 'text/plain',
        allowable_content_types = ('text/plain',),

        widget=TextAreaWidget(
            label="Query",
        ),
        required=1
    ),
))

SparqlSchema = getattr(base.ATCTContent, 'schema', Schema(())).copy() + \
        SparqlBaseSchema.copy()

SparqlSchema['title'].storage = atapi.AnnotationStorage()
SparqlSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(SparqlSchema, moveDiscussion=False)

SparqlBookmarksFolderSchema = getattr(ATFolder, 'schema', Schema(())).copy() + \
        SparqlBaseSchema.copy()
SparqlBookmarksFolderSchema['sparql_query'].widget.description = \
        'The query should return label, bookmark url, query'

def cacheKeySparql(fun, self):
    """ Cache key for Sparql Query """
    return str(self.getArg_spec()) + str(self.getSparql_query())


class Sparql(base.ATCTContent, ZSPARQLMethod):
    """Sparql"""
    implements(ISparql, IVersionEnhanced)

    meta_type = "Sparql"
    schema = SparqlSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    security = ClassSecurityInfo()

    security.declarePublic('index_html')
    def index_html(self, REQUEST=None, **kwargs):
        """index_html"""
        return self.REQUEST.response.redirect(self.absolute_url()+"/@@view")

    @property
    def query(self):
        """query"""
        return self.sparql_query()

    security.declarePublic("execute_query")
    @cache(get_key=cacheKeySparql)
    def execute_query(self, args=None):
        """execute query"""
        arg_spec = parse_arg_spec(self.arg_spec)
        arg_values = map_arg_values(arg_spec, args)[1]
        return self.execute(**self.map_arguments(**arg_values))


class SparqlBookmarksFolder(ATFolder, Sparql):
    """Sparql Bookmarks Folder"""
    implements(ISparqlBookmarksFolder)
    meta_type = "SparqlBookmarksFolder"
    schema = SparqlBookmarksFolderSchema

    def checkQuery(self, title, endpoint, query):
        """Check if a query already exists
           0 - missing
           1 - exists
           2 - exists but changed"""

        found = False
        changed = True
        for sparql in self.values():
            if sparql.title == title:
                found = True
                if sparql.query == query:
                    changed = False
        if not found:
            return 0
        else:
            if not changed:
                return 1
            else:
                return 2

    def addOrUpdateQuery(self, title, endpoint, query):
        """Update an already existing query
           Create new version"""

        ob = None

        changed = True
        for sparql in self.values():
            if sparql.title == title:
                ob = sparql
                if sparql.query == query:
                    changed = False

        if not ob:
            _id = self.generateUniqueId("Sparql")
            _id = self.invokeFactory(type_name="Sparql", id=_id)
            ob = self[_id]
            ob.edit(
                title          = title,
                endpoint_url   = endpoint,
                sparql_query   = query,
            )
            ob._renameAfterCreation(check_auto_id=True)
        else:
            if changed:
                ob = versions.create_version(ob)
                ob.edit(
                    sparql_query   = query,
                )

        return ob

    def syncQueries(self):
        """sync all queries from bookmarks"""
        queries = self.execute()['rows']
        for query in queries:
            query_name = query[0].value
            query_sparql = query[2].value
            self.addOrUpdateQuery(query_name,
                     self.endpoint_url,
                     query_sparql)

atapi.registerType(Sparql, PROJECTNAME)
atapi.registerType(SparqlBookmarksFolder, PROJECTNAME)
