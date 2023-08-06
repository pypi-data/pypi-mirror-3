""" Convert sparql results to json
"""

import sparql
from Products.ZSPARQLMethod import Method

#define our own converters
sparql_converters = Method.sparql_converters.copy()
sparql_converters[sparql.XSD_DECIMAL] = float
sparql_converters[sparql.XSD_DATE] = str
sparql_converters[sparql.XSD_DATETIME] = str
sparql_converters[sparql.XSD_TIME] = str

propertytype_dict = {
                 '': 'text',
                 sparql.XSD_STRING : 'text',
                 sparql.XSD_INTEGER : 'number',
                 sparql.XSD_INT : 'number',
                 sparql.XSD_LONG : 'number',
                 sparql.XSD_DOUBLE : 'number',
                 sparql.XSD_FLOAT : 'number',
                 sparql.XSD_DECIMAL : 'number',
                 sparql.XSD_DATETIME : 'datetime',
                 sparql.XSD_DATE : 'date',
                 sparql.XSD_TIME : 'time',
                 sparql.XSD_BOOLEAN : 'boolean'
                 }

class MethodResult (Method.MethodResult):
    """Override MethodResult with our sparql_converters"""
    def __iter__(self):
        return (sparql.unpack_row(r, convert_type=sparql_converters)
                for r in self.rdfterm_rows)

    def __getitem__(self, n):
        return sparql.unpack_row(self.rdfterm_rows[n],
                                 convert_type=sparql_converters)

def sparql2json(data):
    """ test the converter
        >>> from eea.sparql.converter import sparql2json
        >>> from eea.sparql.tests import mock_data
        >>> from eea.sparql.converter.sparql2json import sparql2json
        >>> test_data = mock_data.loadSparql()
        >>> data = sparql2json(test_data)
        >>> print (data['items'])
        [{'name': u'NAME',
        'double': 2.5,
        'decimal': 5.21,
        'float': 4.5,
        'long': 15,
        'label': 1,
        'boolean': True,
        'time': '2012-01-10 14:31:27',
        'date': '14:31:03',
        'integer': 1,
        'datetime': '2012-01-10',
        'string': u'STRING'},
        {'name': u'',
        'double': 0.0,
        'decimal': 0.0,
        'float': 0.0,
        'long': 0,
        'label': 2,
        'boolean': False,
        'time': '',
        'date': '',
        'integer': 0,
        'datetime': '',
        'string': u''}]

    """
    items = []
    hasLabel = False
    mr = MethodResult(data)

    cols = mr.var_names
    properties = {}

    idx = 0
    for col in cols:
        if col.lower().endswith("label"):
            cols[idx] = 'label'
            hasLabel = True
        idx += 1

    index = 0
    for row in mr:
        index += 1

        rowdata = {}
        if not hasLabel:
            rowdata['label'] = index
        idx = 0
        for item in row:
            rowdata[cols[idx].encode('utf8')] = item
            if (index == 1):
                propertyValueType = 'text'
                if isinstance(data['rows'][0][idx], sparql.Literal):
                    datatype = data['rows'][0][idx].datatype
                    if not datatype:
                        datatype = ''
                    propertyValueType = propertytype_dict[datatype]
                else:
                    if isinstance(data['rows'][0][idx], sparql.IRI):
                        propertyValueType = 'url'
                    else:
                        propertyValueType = 'text'
                properties[cols[idx].encode('utf8')] = \
                    {"valueType" : propertyValueType}
            idx += 1

        items.append(rowdata)
    return {'items':items, 'properties':properties}
