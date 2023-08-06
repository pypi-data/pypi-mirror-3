#!/usr/bin/python
import sparql
import time

querytop = """
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?top ?label
FROM <http://www.eionet.europa.eu/gemet/gemet.rdf.gz>
WHERE {
  <http://www.eionet.europa.eu/gemet/gemetThesaurus> skos:hasTopConcept ?top .
  ?top rdfs:label ?label
} ORDER BY ?label
"""

querymid = """
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?narrower ?label
FROM <http://www.eionet.europa.eu/gemet/gemet.rdf.gz>
WHERE {
  <%s> skos:narrower ?narrower .
  ?narrower rdfs:label ?label
} ORDER BY ?label
"""

endpoint = "http://semantic.eea.europa.eu/sparql"
s = sparql.Service(endpoint)

def print_mid(s, url):
    time.sleep(1)
    print querymid % url
    mid = sparql.query(endpoint, querymid % url)
    for row in mid.fetchall():
        print "%-30s" % row[1],
        print_mid(s, str(row[0]))
        print

top = s.query(querytop)
for row in top.fetchall():
    print "%-30s" % row[1],
    print_mid(s, str(row[0]))
    print
    
