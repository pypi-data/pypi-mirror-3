#!/usr/bin/python
import sparql

querytemplate = """
PREFIX e: <http://eunis.eea.europa.eu/rdf/species-schema.rdf#>
PREFIX dwc: <http://rs.tdwg.org/dwc/terms/>

SELECT xsd:double(?code) AS ?code ?eunisname ?eunisauthor ?valid
WHERE {
  ?eunisurl e:speciesCode ?code;
        e:validName ?valid;
        e:binomialName ?eunisname;
        dwc:scientificNameAuthorship ?eunisauthor.
} LIMIT 10
"""

endpoint = "http://semantic.eea.europa.eu/sparql"
s = sparql.Service(endpoint)

result = s.query(querytemplate)
variables = result.variables

schema = {} # The information for the schema
for var in variables:
    schema[var] = ['', 0]

# xsd:string is more generic than xsd:double
# xsd:string is more generic than xsd:datetime
# xsd:double is more generic than xsd:int
prio = {
  sparql.XSD_STRING : 10,
  sparql.XSD_DECIMAL : 9,
  sparql.XSD_DOUBLE : 8,
  sparql.XSD_INTEGER : 3,
  sparql.XSD_INT : 2
}

def investigateType(name, value):
    if isinstance(value, sparql.IRI) or isinstance(value, sparql.BlankNode):
        schema[name] = [sparql.XSD_STRING, max(schema[name][1], len(unicode(value)))]
    elif isinstance(value, sparql.Literal):
        if schema[name][0] == sparql.XSD_STRING:
            schema[name] = [sparql.XSD_STRING, max(schema[name][1], len(unicode(value)))]
        elif value.datatype in (None, sparql.XSD_STRING, sparql.XSD_DATETIME):
            schema[name] = [sparql.XSD_STRING, max(schema[name][1], len(unicode(value)))]
        elif value.datatype in (sparql.XSD_INT, sparql.XSD_INTEGER) and schema[name][0] != sparql.XSD_STRING:
            schema[name] = [value.datatype, max(schema[name][1], len(unicode(value)))]
        elif value.datatype in (sparql.XSD_DECIMAL, sparql.XSD_DOUBLE) and schema[name][0] != sparql.XSD_STRING:
            schema[name] = [value.datatype, max(schema[name][1], len(unicode(value)))]
            

print """<?xml version="1.0" encoding="UTF-8"?>
<root xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <dataroot>"""
for row in result.fetchone():
    print "<resources>"
    for col in xrange(len(row)):
        investigateType(variables[col], row[col])
        print """ <%s>%s</%s>""" % (variables[col], unicode(row[col]), variables[col])
    print "</resources>"
print """  </dataroot>
  <xsd:schema>
    <xsd:element name="dataroot">
      <xsd:complexType>
        <xsd:sequence>
          <xsd:element ref="resources" minOccurs="0" maxOccurs="unbounded"/>
        </xsd:sequence>
      </xsd:complexType>
    </xsd:element>
    <xsd:element name="resources">
      <xsd:complexType>
        <xsd:sequence>"""
for var in variables:
    datatype = schema[var][0].replace("http://www.w3.org/2001/XMLSchema#","xsd:")
    if datatype == '': datatype = 'xsd:string'
    if datatype == 'xsd:string':
        print """          <xsd:element name="%s" minOccurs="0">
            <xsd:simpleType>
              <xsd:restriction base="%s">
                <xsd:maxLength value="%d"/>
              </xsd:restriction>
            </xsd:simpleType>
          </xsd:element>""" % (var, datatype, schema[var][1])
    else:
        print """          <xsd:element name="%s" minOccurs="0" type="%s"/>""" % (var, datatype)
print """        </xsd:sequence>
      </xsd:complexType>
    </xsd:element>
  </xsd:schema>
</root>"""
