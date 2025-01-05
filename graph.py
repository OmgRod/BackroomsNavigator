"""
Graph creation and Plotly figure generation for the Backrooms Navigator.
"""

import pandas as pd
import plotly.graph_objects as go
import networkx as nx
from config import Config

def create_graph(csv_file):
    """Create the graph using NetworkX."""
    data = pd.read_csv(csv_file)
    graph = nx.Graph()
    defined_nodes = set()
    all_nodes = set()

    for _, row in data.iterrows():
        graph.add_node(row['id'], label=row['name'], difficulty=row['difficulty'], url=row['url'], lvltype=row['lvltype'])
        defined_nodes.add(row['id'])
        all_nodes.add(row['id'])

        entrances = row['entrances'].split(';')
        exits = row['exits'].split(';')
        connections = entrances + exits

        for connection in connections:
            connection = connection.strip()
            if connection in (".", ""):
                continue
            try:
                connection_id = str(connection)
                graph.add_edge(row['id'], connection_id)
                all_nodes.add(connection_id)
            except ValueError:
                continue

    # Add green nodes for undefined levels
    for node in all_nodes:
        if node not in defined_nodes:
            graph.add_node(node, label=node, difficulty='N/A', url='', lvltype='undefined')

    pos = nx.spring_layout(graph, seed=42, k=0.5, iterations=200)
    scale_x = 1.5
    scale_y = 3.0
    for node in pos:
        pos[node] = (pos[node][0] * scale_x, pos[node][1] * scale_y)

    for node in graph.nodes():
        node_label = graph.nodes[node].get('label', '')
        if node_label == "Level 0":
            pos[node] = (0, -5)
        elif node_label == "The Frontrooms":
            pos[node] = (0, 5)

    return graph, pos, defined_nodes

def get_unique_difficulties(csv_file):
    """Extract unique difficulties from the CSV file."""
    data = pd.read_csv(csv_file)
    difficulties = set(data['difficulty'].dropna().unique())
    return difficulties

def filter_graph_by_level(graph, current_level):
    """Filter the graph to show only the current level and its exits."""
    filtered_graph = nx.Graph()
    if current_level in graph.nodes:
        filtered_graph.add_node(current_level, **graph.nodes[current_level])
        for neighbor in graph.neighbors(current_level):
            filtered_graph.add_node(neighbor, **graph.nodes[neighbor])
            filtered_graph.add_edge(current_level, neighbor)
    return filtered_graph

def filter_graph(graph, selected_types, selected_difficulties, show_green_nodes=True):
    """Filter the graph based on selected level types and difficulties."""
    filtered_graph = nx.Graph()
    for node in graph.nodes():
        node_data = graph.nodes[node]
        lvltype = node_data.get('lvltype', 'undefined')
        difficulty = node_data.get('difficulty', 'N/A')
        if lvltype in selected_types and difficulty in selected_difficulties:
            filtered_graph.add_node(node, **node_data)
            for neighbor in graph.neighbors(node):
                if neighbor in filtered_graph.nodes:
                    filtered_graph.add_edge(node, neighbor)
        elif show_green_nodes and lvltype == 'undefined':
            filtered_graph.add_node(node, **node_data)
            for neighbor in graph.neighbors(node):
                if neighbor in filtered_graph.nodes:
                    filtered_graph.add_edge(node, neighbor)
    return filtered_graph

def create_plotly_figure(graph, pos, defined_nodes, show_green_nodes=True):
    edge_x = []
    edge_y = []
    for edge in graph.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.append(x0)
        edge_x.append(x1)
        edge_y.append(y0)
        edge_y.append(y1)

    node_x = []
    node_y = []
    node_text = []
    hover_text = []
    node_color = []
    valid_difficulties = []
    urls = []

    for node in graph.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)

        node_label = graph.nodes[node].get('label', str(node))
        node_id = node

        if node not in defined_nodes:
            if show_green_nodes:
                node_color.append("green")
                node_text.append(f"{node_label}")
                hover_text.append("(Undefined Level)<br>Difficulty: N/A")
                urls.append("")
        else:
            if node_id == node_label:
                node_text.append(f"{node_id}")
            else:
                node_text.append(f"{node_id}<br>{node_label}")

            node_difficulty = graph.nodes[node].get('difficulty', 'N/A')
            if node_difficulty in Config.DIFFICULTY_TYPES:
                hover_text.append(f"Difficulty: {Config.DIFFICULTY_TYPES[node_difficulty]}")
                node_color.append(Config.DIFFICULTY_COLORS[node_difficulty])
            else:
                hover_text.append(f"Difficulty: {node_difficulty}")
                try:
                    difficulty = int(node_difficulty)
                except ValueError:
                    difficulty = 0
                node_color.append(difficulty)
                valid_difficulties.append(difficulty)

            urls.append(graph.nodes[node].get('url', ""))

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y,
        mode='lines',
        line={"width": 0.5, "color": 'gray'},
        hoverinfo='none'
    ))

    scatter = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        marker={
            "size": 10,
            "color": node_color,
            "cmin": min(valid_difficulties, default=0),
            "cmax": max(valid_difficulties, default=5),
            "colorscale": [
                [0, "blue"],
                [0.5, "#FFA07A"],
                [1, "red"]
            ],
            "colorbar": {"title": 'Difficulty'}
        },
        text=node_text,
        textposition="top center",
        hoverinfo='text',
        hovertext=hover_text,
        customdata=urls,
        line={"width": 2, "color": 'black'}
    )
    fig.add_trace(scatter)

    fig.update_layout(
        title="Backrooms Map",
        showlegend=False,
        hovermode='closest',
        xaxis={"showgrid": False, "zeroline": False},
        yaxis={"showgrid": False, "zeroline": False},
        dragmode="zoom",
        autosize=True,
        margin={"l": 0, "r": 0, "t": 40, "b": 0},
        clickmode="event+select"
    )

    return fig

def find_best_exit(graph, current_level, max_difficulty, include_variable, max_entity_count):
    """Find the best exit based on the criteria."""
    best_exit = None
    best_score = float('inf')
    for neighbor in graph.neighbors(current_level):
        neighbor_data = graph.nodes[neighbor]
        difficulty = neighbor_data.get('difficulty', 'N/A')
        if difficulty == '?':
            difficulty = float('inf') if not include_variable else max_difficulty
        elif difficulty == 'var':
            difficulty = max_difficulty if include_variable else float('inf')
        else:
            difficulty = int(difficulty)
        entity_count = neighbor_data.get('entity_count', 0)
        score = difficulty + entity_count
        if score < best_score and difficulty <= max_difficulty and entity_count <= max_entity_count:
            best_score = score
            best_exit = neighbor
    return best_exit