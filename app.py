import sys
import os
#sys.path.append(os.path.abspath("."))

import streamlit as st
import json

# Add full path to src/ for Streamlit Cloud compatibility
#sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from graph_builder import build_knowledge_graph
from graph_queries import apply_logical_rule
from prompt_to_rules import extract_rules_from_prompt_llm3
from semantic_matcher import SemanticMatcher

# from src.prompt_to_rules import extract_rules_from_prompt_llm3
# from src.graph_builder import build_knowledge_graph
# from src.graph_queries import apply_logical_rule
# from src.semantic_matcher import SemanticMatcher

import networkx as nx
import matplotlib.pyplot as plt

# Page config
st.set_page_config(page_title="Auto Audience Generator", layout="wide")
st.title("🧠 Auto Audience Generator")

# Load graph and matcher once
@st.cache_resource
def load_graph_and_matcher():
    G = build_knowledge_graph(
        "data/users.csv",
        "data/products.csv",
        "data/orders.csv",
        "data/streaming.csv",
        "graph_schema.json"
    )
    matcher = SemanticMatcher(G)
    return G, matcher

G, matcher = load_graph_and_matcher()

# Input prompt
prompt = st.text_area("Enter your audience description:", "Find crypto enthusiasts")

if st.button("Generate Audience"):
    try:
        rules_obj = extract_rules_from_prompt_llm3(prompt)
        st.subheader("🔍 Extracted Rules")
        st.json(rules_obj)

        for i, rule in enumerate(rules_obj.get("rules", [])):
            st.markdown(f"### 🎯 Audience {i+1}: {rule['name']}")
            audience = apply_logical_rule(G, rule, matcher=matcher)
            st.success(f"Matched Users ({len(audience)}): {sorted(audience)}")

            # Draw subgraph of matched users and their interests
            subG = nx.DiGraph()
            for user in audience:
                subG.add_node(user, color='lightblue')
                for u, v, d in G.out_edges(user, data=True):
                    if d.get("relation") in ["purchased", "watched"]:
                        subG.add_edge(u, v, label=d["relation"])
                        for _, tag_node, tag_data in G.out_edges(v, data=True):
                            if tag_data.get("relation") in ["tagged_as", "about"]:
                                subG.add_edge(v, tag_node, label=tag_data["relation"])

            fig, ax = plt.subplots(figsize=(10, 6))
            pos = nx.spring_layout(subG)
            nx.draw(subG, pos, with_labels=True, node_color='lightgreen', edge_color='gray', node_size=500, ax=ax)
            edge_labels = nx.get_edge_attributes(subG, 'label')
            nx.draw_networkx_edge_labels(subG, pos, edge_labels=edge_labels, ax=ax)
            st.pyplot(fig)

    except Exception as e:
        st.error(f"❌ Failed to generate audience: {str(e)}")
