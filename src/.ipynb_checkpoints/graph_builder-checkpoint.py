import pandas as pd
import networkx as nx
import json

def build_knowledge_graph_from_config(schema_path, data_paths):
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

    # ✅ 2. Inject user attributes separately (age, gender, location)
    if "users" in dataframes:
        for _, row in dataframes["users"].iterrows():
            uid = row["user_id"]
            if G.has_node(uid):
                # Explicitly assign attributes
                G.nodes[uid]["age"] = int(row["age"]) if not pd.isna(row["age"]) else None
                G.nodes[uid]["gender"] = row["gender"] if not pd.isna(row["gender"]) else None
                G.nodes[uid]["location"] = row["location"] if not pd.isna(row["location"]) else None

    # 3. Create edges
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
