# -*- coding: utf-8 -*-

import sparql

# This query extracts the list of AirBase stations from Content Registry.
# To get the publishing code of the country instead of the ISO code use:
# _:ucountry eea:publishingCode ?country
# To test: append "LIMIT 10" to the end of the query.
querytemplate = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX airbase: <http://rdfdata.eionet.europa.eu/airbase/schema/>
PREFIX eea: <http://rdfdata.eionet.europa.eu/eea/ontology/>
PREFIX geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>

SELECT ?country ?code ?name ?local_code ?station_type ?area_type ?latitude ?longitude ?altitude ?enddate
FROM <http://rdfdata.eionet.europa.eu/airbase/stations.rdf>
FROM <http://rdfdata.eionet.europa.eu/eea/countries.rdf>
WHERE {
 ?stationUrl a airbase:Station;
        airbase:country _:ucountry;
        airbase:eoi_code ?code;
        airbase:name ?name;
        airbase:local_code ?local_code;
        airbase:station_type_eoi ?station_type;
        airbase:area_type_eoi ?area_type;
        airbase:area_type_eoi ?area_type;
        geo:lat ?latitude;
        geo:long ?longitude;
        geo:alt ?altitude.
 OPTIONAL { ?stationUrl airbase:station_end_date ?enddate }
 _:ucountry eea:code ?country
} ORDER BY ?code
"""
s = sparql.Service("http://cr.eionet.europa.eu/sparql")

result = s.query(querytemplate)
for row in result.fetchone():
    print "\t".join(map(unicode,row))

