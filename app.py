"""
Dash application setup and callbacks for the Backrooms Navigator.
"""

from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State
from flask import request
from graph import create_graph, create_plotly_figure, filter_graph_by_level, filter_graph, find_best_exit
from utils import Utils
from config import Config
import webbrowser

# Create the graph and Plotly figure for the default CSV file
default_csv = 'data/mghc.csv'
G, pos, defined_nodes = create_graph(default_csv)
fig = create_plotly_figure(G, pos, defined_nodes)

# Create Dash app
app = Dash(__name__)
server = app.server

# Add custom CSS to hide the Dash button
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <meta property="og:title" content="Backrooms Navigator">
        <meta property="og:description" content="Look at a map of all the levels of the Backrooms and find your way out!">
        <meta property="og:image:secure_url" content="https://omgrod.me/BackroomsNavigator/assets/promo.png">
        <meta property="og:type" content="website">
        <style>
            /* Hide the Dash button */
            .dash-debug-menu {
                display: none;
            }
            /* Ensure the body and html take up the full height */
            html, body {
                height: 100%;
                margin: 0;
                overflow: hidden;
            }
            /* Ensure the main container takes up the full height */
            #root {
                height: 100%;
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

level_ids = Utils.get_level_ids(default_csv)

app.layout = html.Div([
    html.Div([
        html.H2("Graph Switcher"),
        dcc.Dropdown(
            id='csv-file-switcher',
            options=[{'label': name, 'value': f'data/{csv_file}'} for csv_file, name in Config.CSV_FILES.items()],
            value=default_csv,
            clearable=False
        ),
        html.H2("Filters"),
        dcc.Checklist(
            id='level-type-filter',
            options=[
                {'label': 'Normal', 'value': 'normal'},
                {'label': 'Negative', 'value': 'negative'},
                {'label': 'Sublevel', 'value': 'sub'},
                {'label': 'Anomalous', 'value': 'anomalous'}
            ],
            value=['normal', 'negative', 'sub', 'anomalous'],
            labelStyle={'display': 'block'}
        ),
        html.H2("Difficulty"),
        dcc.Dropdown(
            id='difficulty-filter',
            options=[
                {'label': 'Undetermined', 'value': '?'},
                {'label': 'Variable', 'value': 'var'},
                {'label': 'Translation Error', 'value': 'TRANSLATION_ERROR'},
                {'label': 'Integral', 'value': '∫'},
                {'label': 'N/A', 'value': 'N/A'},
                {'label': '0', 'value': '0'},
                {'label': '1', 'value': '1'},
                {'label': '2', 'value': '2'},
                {'label': '3', 'value': '3'},
                {'label': '4', 'value': '4'},
                {'label': '5', 'value': '5'},
                {'label': '10e', 'value': '10e'},
            ],
            value=['?', 'var', 'TRANSLATION_ERROR', '∫', 'N/A', '0', '1', '2', '3', '4', '5'],
            multi=True
        ),
        html.H2("Options"),
        dcc.Checklist(
            id='show-green-nodes',
            options=[
                {'label': 'Show Green Nodes', 'value': 'show'}
            ],
            value=['show'],
            labelStyle={'display': 'block'}
        ),
        html.H2("Best Exit Finder (Unavailable)"),
        html.Label("Max Difficulty"),
        dcc.Input(id='max-difficulty', type='number', value=5, min=1, max=5),
        html.Label("Include Variable Difficulty?"),
        dcc.RadioItems(
            id='include-variable',
            options=[
                {'label': 'Yes', 'value': 'yes'},
                {'label': 'No', 'value': 'no'}
            ],
            value='yes'
        ),
        html.Label("Max Entity Count"),
        dcc.Input(id='max-entity-count', type='number', value=5, min=0),
        html.Button('Find Best Exit', id='find-best-exit', n_clicks=0, disabled=True),  # Disable the calculator button
        html.Div(id='best-exit-result'),
        html.Label("Enter Level ID:"),
        dcc.Dropdown(
            id='level-id-input',
            options=level_ids,
            placeholder="Select or type a level ID",
            multi=False,
            clearable=True
        ),
        html.Button('Update Graph', id='update-graph', n_clicks=0)
    ], style={'width': '20%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '20px', 'height': '100vh', 'overflowY': 'auto'}),
    html.Div([
        dcc.Graph(id='graph', figure=fig, style={'height': '100vh'}, config={'scrollZoom': True})
    ], style={'width': '75%', 'display': 'inline-block', 'verticalAlign': 'top', 'height': '100vh'})
], style={'height': '100vh', 'overflow': 'hidden'})

@app.callback(
    Output('graph', 'figure'),
    Output('level-id-input', 'options'),
    Input('csv-file-switcher', 'value'),
    Input('update-graph', 'n_clicks'),
    State('level-id-input', 'value'),
    State('level-type-filter', 'value'),
    State('difficulty-filter', 'value'),
    State('show-green-nodes', 'value')
)
def update_graph(csv_file, n_clicks, level_id, selected_types, selected_difficulties, show_green_nodes):
    """Update the graph based on the selected CSV file, current level ID, selected types, and difficulties."""
    G, pos, defined_nodes = create_graph(csv_file)
    if level_id:
        filtered_graph = filter_graph_by_level(G, level_id)
    else:
        filtered_graph = filter_graph(G, selected_types, selected_difficulties, show_green_nodes='show' in show_green_nodes)
    filtered_fig = create_plotly_figure(filtered_graph, pos, defined_nodes, show_green_nodes='show' in show_green_nodes)
    level_ids = Utils.get_level_ids(csv_file)
    return filtered_fig, level_ids

@app.callback(
    Output('best-exit-result', 'children'),
    [Input('find-best-exit', 'n_clicks')],
    [State('max-difficulty', 'value'),
     State('include-variable', 'value'),
     State('max-entity-count', 'value')]
)
def calculate_best_exit(n_clicks, max_difficulty, include_variable, max_entity_count):
    """Calculate the best exit based on the criteria."""
    if n_clicks > 0:
        current_level = 'Level 0'  # Assuming starting from Level 0
        include_variable = include_variable == 'yes'
        best_exit = find_best_exit(G, current_level, max_difficulty, include_variable, max_entity_count)
        if best_exit:
            return f"The best exit is: {best_exit}"
        else:
            return "No suitable exit found."
    return ""

@app.callback(
    Output('graph', 'clickData'),
    [Input('graph', 'clickData')]
)
def open_url(clickData):
    """Open the URL in a new browser tab when a node is clicked."""
    if clickData:
        point = clickData['points'][0]
        url = point['customdata']
        if url:
            webbrowser.open(url)
    return None  # Return None to avoid updating the clickData

# Check if the shutdown route is already defined
if not any(rule.endpoint == 'shutdown' for rule in server.url_map.iter_rules()):
    @server.route('/shutdown', methods=['POST'])
    def shutdown():
        """Shutdown the Flask server."""
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()
        return 'Server shutting down...'

def run_app():
    app.run_server(debug=True)