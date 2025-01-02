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
        connection = connection.strip()  # Remove any leading/trailing whitespace
        if connection == "." or connection == "":  # Skip invalid or empty connections
            continue
        try:
            # Handle both types of connection (entrance or exit) as integer node IDs
            connection_id = str(connection)
            G.add_edge(row['id'], connection_id)
        except ValueError:
            continue  # Skip non-numeric connections (e.g., names)

# Step 3: Generate the position of each node in the graph
# Use spring_layout for natural clustering and set positions
pos = nx.spring_layout(G, seed=42, k=0.5, iterations=200)

# Adjust positions to stretch y-axis and keep connected nodes close
scale_x = 1.5  # Moderate horizontal spread
scale_y = 3.0  # Significant vertical spread
for node in pos:
    pos[node] = (pos[node][0] * scale_x, pos[node][1] * scale_y)

# Manually adjust positions for specific nodes
for node in G.nodes():
    node_label = G.nodes[node].get('label', '')
    if node_label == "Level 0":
        pos[node] = (0, -5)  # Place Level 0 at the bottom
    elif node_label == "The Frontrooms":
        pos[node] = (0, 5)  # Place The Frontrooms at the top

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

# Prepare data for the nodes
node_x = []
node_y = []
node_text = []
hover_text = []
node_color = []
valid_difficulties = []  # List to store valid difficulty values

for node in G.nodes():
    x, y = pos[node]
    node_x.append(x)
    node_y.append(y)

    # Node label for display below the ID
    node_label = G.nodes[node].get('label', f'{node}')
    node_id = node  # Assume 'node' itself is the ID
    node_text.append(f"{node_id}<br>{node_label}")  # Display ID and name below

    # Check if difficulty is "?" and update hover text accordingly
    node_difficulty = G.nodes[node].get('difficulty', 'N/A')
    if node_difficulty == "?":
        hover_text.append("Difficulty: Undetermined")
        node_color.append("black")  # Set color to black for undetermined difficulty
    else:
        hover_text.append(f"Difficulty: {node_difficulty}")
        # Ensure node_difficulty is treated as a string for the isdigit check
        if isinstance(node_difficulty, str) and node_difficulty.isdigit():
            difficulty = int(node_difficulty)
        else:
            difficulty = int(node_difficulty) if isinstance(node_difficulty, int) else 0
        
        node_color.append(difficulty)
        valid_difficulties.append(difficulty)  # Add to valid difficulties for the scale

# Step 5: Plot using Plotly for interactive map
fig = go.Figure()

# Add edges to the plot
fig.add_trace(go.Scatter(
    x=edge_x, y=edge_y,
    mode='lines',
    line=dict(width=0.5, color='gray'),
    hoverinfo='none'
))

# Add nodes to the plot with adjusted text and hover info
fig.add_trace(go.Scatter(
    x=node_x, y=node_y,
    mode='markers+text',
    marker=dict(
        size=10,
        color=node_color,
        cmin=min(valid_difficulties, default=0),  # Minimum value for the colorscale
        cmax=max(valid_difficulties, default=5),  # Maximum value for the colorscale
        colorscale=[
            [0, "blue"],  # Difficulty 0: blue
            [0.5, "#FFA07A"],  # Mid-range (2.5): light salmon
            [1, "red"]  # Difficulty 5: dark-ish red
        ],
        colorbar=dict(title='Difficulty')
    ),
    text=node_text,  # Show ID and name below the node
    textposition="top center",
    hoverinfo='text',  # Show only hover text
    hovertext=hover_text  # Specify the hover text separately
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
