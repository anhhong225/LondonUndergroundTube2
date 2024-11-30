import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

class TubeMap:
    def __init__(self, data_file, line_colors):
        self.data_file = data_file
        self.line_colors = line_colors
        self.all_edges = {}  # Store edges by line
        self.node_positions = {}
        self.G = nx.Graph()  # The full graph with all data

    def load_data(self):
        """Load tube line data from CSV and categorize by line."""
        data = pd.read_csv(self.data_file)  
        for _, row in data.iterrows():
            # Store positions
            self.node_positions[row['From Station']] = (row['Longitude_From'], row['Latitude_From'])
            self.node_positions[row['To Station']] = (row['Longitude_To'], row['Latitude_To'])

            # Add to the full graph
            self.G.add_node(row['From Station'], pos=self.node_positions[row['From Station']])
            self.G.add_node(row['To Station'], pos=self.node_positions[row['To Station']])
            self.G.add_edge(
                row['From Station'],
                row['To Station'],
                weight=row['Distance (km)'],
                line=row['Tube Line']
            )

            # Categorize edges by line
            if row['Tube Line'] not in self.all_edges:
                self.all_edges[row['Tube Line']] = []
            self.all_edges[row['Tube Line']].append((row['From Station'], row['To Station']))

    def build_graph(self, selected_lines):
        """Create a new graph for only the selected lines."""
        G = nx.Graph()
        for line in selected_lines:
            if line in self.all_edges:
                for edge in self.all_edges[line]:
                    G.add_edge(edge[0], edge[1], line=line)
        # Add positions to the nodes
        for node in G.nodes():
            G.nodes[node]['pos'] = self.node_positions[node]
        return G

    def plot_selected_lines(self, selected_lines):
        """Plot only the selected lines with accumulated node colors from all selected lines."""
        # Dynamically build the graph for selected lines
        G_selected = self.build_graph(selected_lines)
        pos = nx.get_node_attributes(G_selected, 'pos')

        # Map each node to a list of colors
        node_colors = {}
        for line in selected_lines:
            if line in self.line_colors:
                color = self.line_colors[line]
                edges = [
                    (u, v) for u, v, d in G_selected.edges(data=True)
                    if d['line'] == line
                ]
                for u, v in edges:
                    # If the node is already in the dictionary, append the color
                    if u not in node_colors:
                        node_colors[u] = set()  # Initialize a set to store unique colors
                    if v not in node_colors:
                        node_colors[v] = set()

                    # Add the current line's color to the node
                    node_colors[u].add(color)
                    node_colors[v].add(color)

        # For nodes with multiple colors, use a mixture or gradient, or a specific strategy
        node_color_list = []
        for node in G_selected.nodes:
            # Take the first color or a mix of colors (this example just takes the first color)
            color = list(node_colors.get(node, {"lightgray"}))[0]
            node_color_list.append(color)

        # Plot the graph
        plt.figure(figsize=(12, 10))
        line_handles = []  # To store the handles for the legend

        # Draw edges and create the legend for each line
        for line in selected_lines:
            if line in self.line_colors:
                color = self.line_colors[line]
                edges = [
                    (u, v) for u, v, d in G_selected.edges(data=True)
                    if d['line'] == line
                ]
                nx.draw_networkx_edges(G_selected, pos, edgelist=edges, edge_color=color, width=2.5, alpha=0.8)
                # Create a legend entry for each line
                line_handles.append(plt.Line2D([0], [0], color=color, lw=2, label=line))

        # Draw nodes with the accumulated colors
        nx.draw_networkx_nodes(G_selected, pos, node_size=70, node_color=node_color_list)

        # Add labels
        nx.draw_networkx_labels(G_selected, pos, font_size=8)

        # Add the legend
        plt.legend(handles=line_handles, loc='upper right')

        plt.axis("off")
        plt.tight_layout()
        return plt.gcf()

    def plot_all_lines(self):
        """Plot the entire map with all tube lines. Nodes will take the color of their connected lines."""
        pos = nx.get_node_attributes(self.G, 'pos')

        # Map each node to a line color
        node_colors = {}
        for line, color in self.line_colors.items():
            edges = [
                (u, v) for u, v, d in self.G.edges(data=True)
                if d['line'] == line
            ]
            for u, v in edges:
                if u not in node_colors:
                    node_colors[u] = color  # Assign the node to the line's color
                if v not in node_colors:
                    node_colors[v] = color

        # Generate a color list for all nodes in the graph
        node_color_list = [node_colors.get(node, "lightgray") for node in self.G.nodes]

        plt.figure(figsize=(12, 10))

        line_handles = []  # To store the handles for the legend

        # Draw edges and create the legend for each line
        for line, color in self.line_colors.items():
            edges = [
                (u, v) for u, v, d in self.G.edges(data=True)
                if d['line'] == line
            ]
            nx.draw_networkx_edges(self.G, pos, edgelist=edges, edge_color=color, width=1.5, alpha=0.6)
            # Create a legend entry for each line
            line_handles.append(plt.Line2D([0], [0], color=color, lw=2, label=line))

        # Draw nodes with their assigned colors
        nx.draw_networkx_nodes(self.G, pos, node_size=50, node_color=node_color_list)

        # Optionally, add labels
        nx.draw_networkx_labels(self.G, pos, font_size=8)

        # Add the legend
        plt.legend(handles=line_handles, loc='upper right')

        plt.axis("off")
        plt.tight_layout()
        return plt.gcf()