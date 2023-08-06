from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart

d = Drawing(300, 200)

chart = VerticalBarChart()
chart.width = 260
chart.height = 160
chart.x = 20
chart.y = 20
chart.data = [[1,2], [3,4]]
chart.categoryAxis.categoryNames = ['foo', 'bar']
chart.valueAxis.valueMin = 0

d.add(chart)
d.save(fnRoot='test', formats=['png'])

