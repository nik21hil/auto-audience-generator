import sys
import os
import json
import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
from io import StringIO

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))
from graph_builder import build_knowledge_graph_from_config
from graph_queries import apply_logical_rule
from prompt_to_rules import extract_rules_from_prompt_llm3
from semantic_matcher import SemanticMatcher

# Page Setup
st.set_page_config(
    page_title="Auto Audience Generator",
    page_icon="https://raw.githubusercontent.com/nik21hil/auto-audience-generator/main/assets/ns_logo1_transparent.png",
)

st.markdown(
    """
    <div style="display: flex; justify-content: center; align-items: center; gap: 15px; margin-bottom: 5px;">
        <img src="https://raw.githubusercontent.com/nik21hil/auto-audience-generator/main/assets/ns_logo1_transparent.png" width="100">
        <h1 style="margin: 0; font-size: 48px;">Auto Audience Generator</h1>
    </div>
    <p style="text-align: center; color: gray; font-size: 15px; margin-top: -10px; margin-bottom: 1px;">
        A lightweight, no-code interface to build audience based on defined persona.
    </p>
    """,
    unsafe_allow_html=True
)
st.markdown("---")

# Load Graph
#st.cache_resource
def load_graph_and_matcher():
    G = build_knowledge_graph_from_config(
        "src/graph_schema.json",
        {
            "users": "data/users.csv",
            "products": "data/products.csv",
            "orders": "data/orders.csv",
            "streaming": "data/streaming.csv"
        }
    )
    matcher = SemanticMatcher(G)
    return G, matcher

G, matcher = load_graph_and_matcher()

# State initialization
if "rule_obj" not in st.session_state:
    st.session_state.rule_obj = None
if "audience" not in st.session_state:
    st.session_state.audience = None

# UI Inputs
st.markdown("###### ✍️ Enter your audience description:")
prompt = st.text_area(label="", value="Find sports fans")

cols = st.columns(3)
with cols[0]:
    if st.button("🧠 Create Rule"):
        with st.spinner("Thinking..."):
            rule_obj = extract_rules_from_prompt_llm3(prompt)
            if "error" in rule_obj:
                st.session_state.rule_obj = None
                st.error("❌ LLM failed to return clean JSON.")
                st.code(rule_obj["raw_response"])
            else:
                st.session_state.rule_obj = rule_obj
                st.success("✅ Rule created successfully.")

with cols[1]:
    if st.button("🎯 Generate Audience"):
        if st.session_state.rule_obj is None:
            st.warning("⚠️ Please create a rule first.")
        else:
            with st.spinner("Filtering audience..."):
                rule = {"conditions": st.session_state.rule_obj.get("conditions", {})}
                st.session_state.audience = apply_logical_rule(G, rule, matcher=matcher)

with cols[2]:
    if st.button("🌐 Visualize Graph"):
        if st.session_state.audience:
            with st.spinner("Rendering graph..."):
                subG = nx.DiGraph()
                for user in st.session_state.audience:
                    subG.add_node(user, color='lightblue')
                    for u, v, d in G.out_edges(user, data=True):
                        if d.get("relation") in ["purchased", "watched"]:
                            subG.add_edge(u, v, label=d["relation"])
                            for _, tag_node, tag_data in G.out_edges(v, data=True):
                                if tag_data.get("relation") in ["tagged_as", "about"]:
                                    subG.add_edge(v, tag_node, label=tag_data["relation"])

                fig, ax = plt.subplots(figsize=(6, 4))
                pos = nx.spring_layout(subG, k=0.3)
                nx.draw(subG, pos, with_labels=True, node_color='lightgreen', edge_color='gray', node_size=300, font_size=8, ax=ax)
                edge_labels = nx.get_edge_attributes(subG, 'label')
                nx.draw_networkx_edge_labels(subG, pos, edge_labels=edge_labels, font_size=6, ax=ax)
                st.pyplot(fig)
        else:
            st.warning("⚠️ No audience generated yet.")

# Rule Display
if st.session_state.rule_obj and "conditions" in st.session_state.rule_obj:
    def display_conditions(cond, indent=0):
        html = ""
        pad = "&nbsp;" * 4 * indent
        if "and" in cond:
            html += f"{pad}<b>AND</b><br>"
            for c in cond["and"]:
                html += display_conditions(c, indent + 1)
        elif "or" in cond:
            html += f"{pad}<b>OR</b><br>"
            for c in cond["or"]:
                html += display_conditions(c, indent + 1)
        else:
            field = cond.get("field", "")
            values = cond.get("in", [])
            op = cond.get("operator", "in")
            val = cond.get("value")
            if op == "in":
                html += f"{pad}• <code>{field}</code> in {values}<br>"
            else:
                html += f"{pad}• <code>{field}</code> {op} {val}<br>"
        return html

    with st.expander("🔍 Show Extracted Rule", expanded=False):
        rule_html = display_conditions(st.session_state.rule_obj["conditions"])
        st.markdown(rule_html, unsafe_allow_html=True)

# Audience Display
if st.session_state.audience is not None:
    st.markdown("### ✅ Total Matched Users: " + str(len(st.session_state.audience)))
    sample_df = pd.DataFrame({"user_id": sorted(list(st.session_state.audience))[:10]})
    st.markdown("#### 👥 Sample Users:")
    st.dataframe(sample_df)

    # CSV download
    full_df = pd.DataFrame({"user_id": sorted(list(st.session_state.audience))})
    csv = full_df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download Full Audience", csv, "audience.csv", "text/csv")