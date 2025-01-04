"""
Main entry point for the Backrooms Navigator application.
"""

import threading
import time
import os
import requests
import argparse
from graph import create_graph, create_plotly_figure
from templates import HTMLTemplates
from config import Config

os.environ["PORT"] = "8050"

def generate_html_files(show_green_nodes=True):
    for csv_file, name in Config.CSV_FILES.items():
        G, pos, defined_nodes = create_graph(f'data/{csv_file}')
        fig = create_plotly_figure(G, pos, defined_nodes, show_green_nodes=show_green_nodes)
        html_content = fig.to_html(full_html=False, include_plotlyjs='cdn')
        html_template = HTMLTemplates.generate_html_template(name, html_content)

        with open(f'index_{csv_file.split(".")[0]}.html', 'w', encoding='utf-8') as f:
            f.write(html_template)

def run_app():
    from app import app
    app.run_server(debug=True)

def main():
    parser = argparse.ArgumentParser(description="Backrooms Navigator CLI")
    parser.add_argument('command', nargs='?', default='run', choices=['run', 'gen'], help="Command to run")
    args = parser.parse_args()

    if args.command == 'gen':
        generate_html_files()
        print("HTML files generated.")
    else:
        run_app()

if __name__ == '__main__':
    main()