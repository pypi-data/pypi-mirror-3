
import urllib

q="""
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX wgs: <http://www.w3.org/2003/01/geo/wgs84_pos#>
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX dbp: <http://dbpedia.org/property/>
PREFIX dbr: <http://dbpedia.org/resource/>
PREFIX sdmx: <http://purl.org/linked-data/sdmx#>
PREFIX sdmx-attribute: <http://purl.org/linked-data/sdmx/2009/attribute#>
PREFIX sdmx-code: <http://purl.org/linked-data/sdmx/2009/code#>
PREFIX sdmx-concept: <http://purl.org/linked-data/sdmx/2009/concept#>
PREFIX sdmx-dimension: <http://purl.org/linked-data/sdmx/2009/dimension#>
PREFIX sdmx-measure: <http://purl.org/linked-data/sdmx/2009/measure#>
PREFIX sdmx-metadata: <http://purl.org/linked-data/sdmx/2009/metadata#>
PREFIX sdmx-subject: <http://purl.org/linked-data/sdmx/2009/subject#>
PREFIX qb: <http://purl.org/linked-data/cube#>
PREFIX year: <http://reference.data.gov.uk/id/year/>
PREFIX fn: <http://www.w3.org/2005/xpath-functions/#>
PREFIX bank: <http://worldbank.270a.info/property/>
PREFIX d-indicators: <http://worldbank.270a.info/dataset/world-development-indicators>

#USE THESE GRAPHS :)
PREFIX g-void: <http://worldbank.270a.info/graph/void>
PREFIX g-meta: <http://worldbank.270a.info/graph/meta>
PREFIX g-climates: <http://worldbank.270a.info/graph/world-bank-climates>
PREFIX g-finances: <http://worldbank.270a.info/graph/world-bank-finances>
PREFIX g-projects: <http://worldbank.270a.info/graph/world-bank-projects-and-operations>
PREFIX g-indicators: <http://worldbank.270a.info/graph/world-development-indicators>

SELECT ?year ?country ?value
WHERE {
?s bank:indicator <http://worldbank.270a.info/classification/indicator/EG.USE.PCAP.KG.OE>.
?s qb:dataSet  d-indicators: .
?s a  qb:Observation.
?s sdmx-measure:obsValue ?value.
?s sdmx-dimension:refArea ?area.
?area bank:income-level <http://worldbank.270a.info/classification/income-level/OEC> .
?area skos:prefLabel ?country.
{
  ?s sdmx-dimension:refPeriod <http://reference.data.gov.uk/id/year/2010>.
  BIND("2010" AS ?year)
} UNION {
  ?s sdmx-dimension:refPeriod <http://reference.data.gov.uk/id/year/2005>.
  BIND("2005" AS ?year)
} UNION {
  ?s sdmx-dimension:refPeriod <http://reference.data.gov.uk/id/year/2000>.
  BIND("2000" AS ?year)
}
} ORDER BY ?year
"""

#print urllib.quote_plus(q,'{}')

server="http://services.data.gov.uk/transport/sparql"
server="http://semantic.data.gov/sparql"
server="http://worldbank.270a.info/sparql"
f=urllib.urlopen(server + "?query=" + urllib.quote_plus(q))
print f.read()

# resulting query
#http://data.gov.uk/sparql?query=PREFIX+rdf%3A+%3Chttp%3A%2F%2Fwww.w3.org%2F1999%2F02%2F22-rdf-syntax-ns%23%3E%0D%0APREFIX+rdfs%3A+%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23%3E%0D%0APREFIX+xsd%3A+%3Chttp%3A%2F%2Fwww.w3.org%2F2001%2FXMLSchema%23%3E%0D%0APREFIX+owl%3A+%3Chttp%3A%2F%2Fwww.w3.org%2F2002%2F07%2Fowl%23%3E%0D%0APREFIX+skos%3A+%3Chttp%3A%2F%2Fwww.w3.org%2F2004%2F02%2Fskos%2Fcore%23%3E%0D%0ASELECT+DISTINCT+%3Fpred+%3Fobj%0D%0A++++WHERE+{%0D%0A++++++%3Chttp%3A%2F%2Ftransport.data.gov.uk%2Fid%2Fstop-point%2F490014854GB%3E+%3Fpred+%3Fobj%0D%0A++++}++++LIMIT+50&datasource=5&dataformat=XML

# Environment:  http://services.data.gov.uk/environment/sparql
#Transport
#wget -O - -q  --header='Accept: application/sparql-results+xml, application/rdf+xml, */*' "http://services.data.gov.uk/transport/sparql?query=PREFIX+rdf%3A+%3Chttp%3A%2F%2Fwww.w3.org%2F1999%2F02%2F22-rdf-syntax-ns%23%3E%0D%0APREFIX+rdfs%3A+%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23%3E%0D%0APREFIX+xsd%3A+%3Chttp%3A%2F%2Fwww.w3.org%2F2001%2FXMLSchema%23%3E%0D%0APREFIX+owl%3A+%3Chttp%3A%2F%2Fwww.w3.org%2F2002%2F07%2Fowl%23%3E%0D%0APREFIX+skos%3A+%3Chttp%3A%2F%2Fwww.w3.org%2F2004%2F02%2Fskos%2Fcore%23%3E%0D%0ASELECT+DISTINCT+%3Fpred+%3Fobj%0D%0A++++WHERE+{%0D%0A++++++%3Chttp%3A%2F%2Ftransport.data.gov.uk%2Fid%2Fstop-point%2F490014854GB%3E+%3Fpred+%3Fobj%0D%0A++++}++++LIMIT+50"

