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
html_content = fig.to_html(full_html=False)

# Add Open Graph meta tags to the HTML content
html_content = f'''
<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <title>Backrooms Navigator</title>
        <meta property="og:title" content="Backrooms Navigator">
        <meta property="og:description" content="Look at a map of all the levels of the Backrooms and find your way out!">
        <meta property="og:image" content="/assets/promo.png">
        <meta property="og:type" content="website">
    </head>
    <body>
        {html_content}
    </body>
</html>
'''

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

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