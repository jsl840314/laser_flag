from plotly.graph_objs import Bar, Layout
from plotly import offline


results = []

for die_1 in range(1, 7):
    for die_2 in range (1, 7):
        # for die_3 in range (1, 7):
        results.append(die_1 * die_2)

rolls = list(range(1, 37))

frequencies = []
for value in range(1, 37):
    frequency = results.count(value)
    frequencies.append(frequency)

# print(rolls)
# print(frequencies)


# Visualize the results.

data = [Bar(x=rolls, y=frequencies)]

x_axis_config = {'title': 'Result'}
y_axis_config = {'title': 'Frequency of Result'}
my_layout = Layout(title='D6 * D6 (36 possible results)',
    xaxis=x_axis_config, yaxis=y_axis_config)
offline.plot({'data': data, 'layout': my_layout}, filename='D6xD6.html')
