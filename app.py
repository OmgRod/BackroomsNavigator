"""
Dash application setup and callbacks for the Backrooms Navigator.
"""

import webbrowser
import pandas as pd
from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State
from flask import request
from graph import create_graph, create_plotly_figure, filter_graph_by_level, filter_graph, find_best_exit

# Create the graph and Plotly figure
G, pos, defined_nodes = create_graph()
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
        <meta property="og:image" content="/assets/promo.png">
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

# Extract level IDs for the dropdown options
level_ids = [{'label': row['id'], 'value': row['id']} for _, row in pd.read_csv('levels.csv').iterrows()]

app.layout = html.Div([
    html.Div([
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
                {'label': '0', 'value': '0'},
                {'label': '1', 'value': '1'},
                {'label': '2', 'value': '2'},
                {'label': '3', 'value': '3'},
                {'label': '4', 'value': '4'},
                {'label': '5', 'value': '5'}
            ],
            value=['?', 'var', 'TRANSLATION_ERROR', '∫', '0', '1', '2', '3', '4', '5'],
            multi=True
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
    [Input('update-graph', 'n_clicks')],
    [State('level-id-input', 'value'),
     State('level-type-filter', 'value'),
     State('difficulty-filter', 'value')]
)
def update_graph(n_clicks, level_id, selected_types, selected_difficulties):
    """Update the graph based on the current level ID, selected types, and difficulties."""
    if level_id:
        filtered_graph = filter_graph_by_level(G, level_id)
    else:
        filtered_graph = filter_graph(G, selected_types, selected_difficulties)
    filtered_fig = create_plotly_figure(filtered_graph, pos, defined_nodes)
    return filtered_fig

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

@server.route('/shutdown', methods=['POST'])
def shutdown():
    """Shutdown the Flask server."""
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return 'Server shutting down...'

def run_app():
    """Run the Dash application."""
    app.run_server(debug=True)

if __name__ == '__main__':
    if CLOSE_SERVER_AFTER_GENERATION:
        # Run the server in a separate thread
        server_thread = threading.Thread(target=run_app)
        server_thread.start()

        # Wait for a short period to ensure the server starts
        time.sleep(5)

        # Generate the HTML file
        app.layout.children[1].children[0].figure.write_html('index.html')

        # Close the server
        import os
        os._exit(0)
    else:
        run_app()