from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import webbrowser
from graph import create_graph, create_plotly_figure

# Create the graph and Plotly figure
G, pos, defined_nodes = create_graph()
fig = create_plotly_figure(G, pos, defined_nodes)

# Create Dash app
app = Dash(__name__)

# Add custom CSS to hide the Dash button
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            /* Hide the Dash button */
            .dash-debug-menu {
                display: none;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

app.layout = html.Div([
    dcc.Graph(id='graph', figure=fig, style={'height': '100vh'})
], style={'height': '100vh'})

@app.callback(
    Output('graph', 'figure'),
    Input('graph', 'clickData')
)
def display_click_data(clickData):
    if clickData:
        point = clickData['points'][0]
        url = point['customdata']
        if url:
            webbrowser.open(url)
    return fig  # Return the figure to avoid updating the clickData

def run_app():
    app.run_server(debug=True)