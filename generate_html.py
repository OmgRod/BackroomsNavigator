from graph import create_graph, create_plotly_figure

G, pos, defined_nodes = create_graph()
fig = create_plotly_figure(G, pos, defined_nodes)
html = fig.to_html(full_html=True)
with open("index.html", "w") as f:
    f.write(html)