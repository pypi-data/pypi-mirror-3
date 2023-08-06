import sparql
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.textlabels import Label

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
data_values = []
linelabels = [] # Must match data_values array
c = ""
data_row = -1
countries = []
for row in result.fetchall():
    if c != unicode(row[0]):
        c = unicode(row[0])
        countries.append(c)
        data_row += 1
        data_col = 0
        data_values.append([])
        linelabels.append([])
    data_values[data_row].append(float(str(row[4])))
    if data_col == 0:
        linelabels[data_row].append(c)
    else:
        linelabels[data_row].append(None)
    data_col += 1

# Calculate Y-labels
data_as_list = []
for d in data_values:
    data_as_list.extend(d)
max_y = int(max(data_as_list))
v_labels = map(str, range(0, max_y + 1, max_y / 6))

d = Drawing(800, 500)

chart = HorizontalLineChart()
chart.width = 760
chart.height = 460
chart.x = 20
chart.y = 20
chart.lineLabelArray = linelabels
chart.lineLabelFormat = 'values'
chart.data = data_values
chart.categoryAxis.categoryNames = h_labels
chart.valueAxis.valueMin = 0

d.add(chart)
d.save(fnRoot='ghg-totals', formats=['png'])

#       x: x-position of lower-left chart origin
#       y: y-position of lower-left chart origin
#       width: chart width
#       height: chart height

#       useAbsolute: disables auto-scaling of chart elements (?)
#       lineLabelNudge: distance of data labels to data points
#       lineLabels: labels associated with data values
#       lineLabelFormat: format string or callback function
#       groupSpacing: space between categories

#       joinedLines: enables drawing of lines

#       strokeColor: color of chart lines (?)
#       fillColor: color for chart background (?)
#       lines: style list, used cyclically for data series

#       valueAxis: value axis object
#       categoryAxis: category axis object
#       categoryNames: category names

#       data: chart data, a list of data series of equal length

