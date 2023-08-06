import sparql, cairo, CairoPlot

querytemplate = """
PREFIX qb: <http://purl.org/linked-data/cube#>
PREFIX e: <http://ontologycentral.com/2009/01/eurostat/ns#>
PREFIX sdmx-measure: <http://purl.org/linked-data/sdmx/2009/measure#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX g: <http://eurostat.linked-statistics.org/ontologies/geographic.rdf#>
PREFIX dataset: <http://eurostat.linked-statistics.org/data/>

SELECT ?nuts2
       SUM(xsd:decimal(?obsvalue)) AS ?population
       ?wateruse
       xsd:decimal(?wateruse)*1000000/SUM(xsd:decimal(?obsvalue)) AS ?percapita
WHERE {
  ?observation qb:dataset dataset:demo_r_pjanaggr3 ;
        e:time <http://eurostat.linked-statistics.org/dic/time#2007>;
        e:age <http://eurostat.linked-statistics.org/dic/age#TOTAL>; 
        e:sex <http://eurostat.linked-statistics.org/dic/sex#T>;
        e:geo ?ugeo;
        sdmx-measure:obsValue ?obsvalue.
  ?ugeo g:hasParentRegion ?parent.
  ?parent g:code ?nuts2.
  ?wuregion qb:dataset dataset:env_n2_wu ;
            e:geo ?parent;
            e:cons <http://eurostat.linked-statistics.org/dic/cons#W18_2_7_2>; 
            e:time <http://eurostat.linked-statistics.org/dic/time#2007>;
        sdmx-measure:obsValue ?wateruse.
} GROUP BY ?nuts2 ?wateruse ORDER BY DESC(?percapita) LIMIT 20
"""
endpoint = "http://semantic.eea.europa.eu/sparql"
s = sparql.Service(endpoint)

result = s.query(querytemplate)
h_labels = []
data = []
for row in result.fetchall():
    h_labels.append(unicode(row[0]))
    data.append(float(str(row[3])))

max_y = int(max(data))
v_labels = map(str, range(0, max_y + 1, max_y / 6))
CairoPlot.bar_plot ('waterusepercapita.png', data, 1000, 500, border = 20,
        grid = True, h_labels = h_labels, v_labels = v_labels)
