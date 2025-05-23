import pandas as pd
import networkx as nx
import json

def build_knowledge_graph_from_config(schema_path, data_paths):
    """
    schema_path: str — path to graph_schema.json
    data_paths: dict — keys like 'users', 'orders', 'products', 'streaming'
                       values are file paths to CSVs
    """
    with open(schema_path, 'r') as f:
        config = json.load(f)

    G = nx.DiGraph()

    # Load all datasets
    dataframes = {k: pd.read_csv(v) for k, v in data_paths.items()}

    # 1. Create all nodes
    for dataset_name, df in dataframes.items():
        for _, row in df.iterrows():
            for col, node_type in config['nodes'].items():
                if col in row:
                    node_id = row[col]
                    if not G.has_node(node_id):
                        G.add_node(node_id, type=node_type)

    # 2. Create edges from config
    for edge in config['edges']:
        src_col = edge['from']
        tgt_col = edge['to']
        relation = edge['relation']
        dataset = edge['via']

        if dataset not in dataframes:
            continue

        for _, row in dataframes[dataset].iterrows():
            if src_col in row and tgt_col in row:
                G.add_edge(row[src_col], row[tgt_col], relation=relation)

    print("✅ Graph successfully created")
    print("Number of nodes:", G.number_of_nodes())
    print("Number of edges:", G.number_of_edges())
    return G
    
