import sparql, cairo, CairoPlot

querytemplate = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX qb: <http://purl.org/linked-data/cube#>
PREFIX e: <http://ontologycentral.com/2009/01/eurostat/ns#>
PREFIX sdmx-measure: <http://purl.org/linked-data/sdmx/2009/measure#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX g: <http://eurostat.linked-statistics.org/ontologies/geographic.rdf#>
PREFIX dataset: <http://eurostat.linked-statistics.org/data/>

SELECT ?country
       ?year
       ?population
       ?ghgtotal
       xsd:decimal(?ghgtotal)*10000/(xsd:decimal(?population)) AS ?percapita
WHERE {
  ?popobs qb:dataset dataset:demo_pjanbroad ;
        e:time ?uyear;
        e:freq <http://eurostat.linked-statistics.org/dic/freq#A>;
        e:age <http://eurostat.linked-statistics.org/dic/age#TOTAL>; 
        e:sex <http://eurostat.linked-statistics.org/dic/sex#T>;
        e:geo ?ucountry;
        sdmx-measure:obsValue ?population.
  ?ghgobs qb:dataset dataset:env_air_gge ;
        e:geo ?ucountry;
        e:time ?uyear;
        e:airsect <http://eurostat.linked-statistics.org/dic/airsect#TOT_X_5>;
        sdmx-measure:obsValue ?ghgtotal.
  ?ucountry skos:prefLabel ?country.
  ?uyear skos:prefLabel ?year
} ORDER BY ?country ?year
"""

endpoint = "http://semantic.eea.europa.eu/sparql"
s = sparql.Service(endpoint)

result = s.query(querytemplate)
h_labels = map(str,range(1990, 2010))
data = {}
c = ""
for row in result.fetchall():
    if c != unicode(row[0]):
        c = unicode(row[0])
        data[c] = []
#   h_labels.append(unicode(row[1]))
    data[c].append(float(str(row[4])))

data_as_list = []
for d in data.values():
    data_as_list.extend(d)
max_y = int(max(data_as_list))
v_labels = map(str, range(0, max_y + 1, max_y / 6))
#print v_labels
CairoPlot.dot_line_plot('ghg-totals.png', data, 1000, 500, border = 20,
        axis = True, dots = True, grid = True, h_labels = h_labels, v_labels = v_labels)
