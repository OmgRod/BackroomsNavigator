"""
Dash application setup and callbacks for the Backrooms Navigator.
"""

import webbrowser
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
from flask import request
from graph import create_graph, create_plotly_figure

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
def display_click_data(click_data):
    """Handle click events on the graph."""
    if click_data:
        point = click_data['points'][0]
        url = point['customdata']
        if url:
            webbrowser.open(url)
    return fig  # Return the figure to avoid updating the clickData

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
