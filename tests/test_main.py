"""
Unit tests for the main module of the Backrooms Navigator application.
"""

from main import create_graph

def test_create_graph():
    """Test the create_graph function."""
    graph, pos, defined_nodes = create_graph()
    assert graph is not None
    assert pos is not None
    assert defined_nodes is not None
