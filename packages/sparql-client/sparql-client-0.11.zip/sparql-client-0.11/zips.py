import sparql, cairo, CairoPlot

querytemplate = """
PREFIX cr: <http://cr.eionet.europa.eu/ontologies/contreg.rdf#>
PREFIX rod: <http://rod.eionet.europa.eu/schema.rdf#>

SELECT * WHERE {
  ?sourcefile a rod:File;
              cr:mediaType "application/zip".
  ?env rod:hasFile ?sourcefile;
       rod:released ?released;
       rod:obligation ?obligation;
       rod:locality _:locality.
  _:locality rod:loccode ?loccode
  FILTER(?obligation IN (<http://rod.eionet.europa.eu/obligations/358>, <http://rod.eionet.europa.eu/obligations/137>))
} ORDER BY DESC(?date) LIMIT 10
"""
endpoint = "http://cr.eionet.europa.eu/sparql"
s = sparql.Service(endpoint)

result = s.query(querytemplate)
for row in result.fetchone():
    print "\t".join(map(str,row))


