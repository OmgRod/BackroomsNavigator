import pandas as pd
import plotly.graph_objects as go
import networkx as nx

# Step 1: Read the CSV file using Pandas
data = pd.read_csv('levels.csv')

# Step 2: Create a Graph using NetworkX
G = nx.Graph()

# Add nodes and edges based on both entrances and exits
for _, row in data.iterrows():
    # Add nodes with 'id', 'label' (name), and 'difficulty'
    G.add_node(row['id'], label=row['name'], difficulty=row['difficulty'])

    # Combine entrances and exits into one list (both can form connections)
    entrances = row['entrances'].split(';')
    exits = row['exits'].split(';')

    # Combine both into one list for connecting nodes
    connections = entrances + exits

    # Add edges for each entrance/exit connection
    for connection in connections:
        try:
            # Handle both types of connection (entrance or exit) as integer node IDs
            connection_id = str(connection)
            G.add_edge(row['id'], connection_id)
        except ValueError:
            continue  # Skip non-numeric connections (e.g., names)

# Step 3: Generate the position of each node in the graph
pos = nx.spring_layout(G, seed=42, k=0.5)  # Increased k for better spacing of nodes

# Step 4: Prepare data for Plotly (nodes and edges)
edge_x = []
edge_y = []
for edge in G.edges():
    x0, y0 = pos[edge[0]]
    x1, y1 = pos[edge[1]]
    edge_x.append(x0)
    edge_x.append(x1)
    edge_y.append(y0)
    edge_y.append(y1)

# Create a scatter plot for the nodes
node_x = []
node_y = []
node_text = []
node_color = []
for node in G.nodes():
    x, y = pos[node]
    node_x.append(x)
    node_y.append(y)

    # Prepare the node text with name and difficulty
    node_label = G.nodes[node].get('label', f'{node}')
    node_difficulty = G.nodes[node].get('difficulty', 'N/A')
    node_text.append(f"{node_label}<br>Difficulty: {node_difficulty}")

    # Color nodes based on difficulty (lighter color for easier levels)
    node_color.append(G.nodes[node].get('difficulty', 1))

# Step 5: Plot using Plotly for interactive map
fig = go.Figure()

# Add edges to the plot
fig.add_trace(go.Scatter(
    x=edge_x, y=edge_y,
    mode='lines',
    line=dict(width=0.5, color='gray'),
    hoverinfo='none'
))

# Add nodes to the plot with color and text
fig.add_trace(go.Scatter(
    x=node_x, y=node_y,
    mode='markers+text',
    marker=dict(size=10, color=node_color, colorscale='Viridis', colorbar=dict(title='Difficulty')),
    text=node_text,
    textposition="top center",
    hoverinfo='text'
))

# Step 6: Layout settings for zoom and dragging
fig.update_layout(
    title="Backrooms Map",
    showlegend=False,
    hovermode='closest',
    xaxis=dict(showgrid=False, zeroline=False),
    yaxis=dict(showgrid=False, zeroline=False),
    dragmode="zoom",  # Allow zoom and drag
    autosize=True,
    margin=dict(l=0, r=0, t=40, b=0),
)

# Step 7: Export to HTML file to view in the browser
fig.write_html("index.html")

# Show plot in notebook (optional)
fig.show()
