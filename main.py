"""
Main entry point for the Backrooms Navigator application.
"""

import threading
import time
import os
import requests
from app import run_app
from graph import create_graph, create_plotly_figure

# Variable to control whether the server should close after generating the HTML file
CLOSE_SERVER_AFTER_GENERATION = False

# Create the graph and Plotly figure
G, pos, defined_nodes = create_graph()
fig = create_plotly_figure(G, pos, defined_nodes)

# Save the Plotly figure as an HTML file
fig.write_html('index.html')

if __name__ == '__main__':
    if CLOSE_SERVER_AFTER_GENERATION:
        # Run the server in a separate thread
        server_thread = threading.Thread(target=run_app)
        server_thread.start()

        # Wait for a short period to ensure the server starts
        time.sleep(5)

        # Make a request to the shutdown route to stop the server
        requests.post('http://127.0.0.1:8050/shutdown')
    else:
        run_app()
