import sys
import os
import streamlit as st
import json
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
from io import StringIO

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))
from graph_builder import build_knowledge_graph_from_config
from graph_queries import apply_logical_rule
from prompt_to_rules import extract_rules_from_prompt_llm3
from semantic_matcher import SemanticMatcher

# Streamlit Page Config
st.set_page_config(
    page_title="Auto Audience Generator",
    page_icon="https://raw.githubusercontent.com/nik21hil/auto-audience-generator/main/assets/ns_logo1_transparent.png",
)

st.markdown("""
    <style>
    /* Completely remove border and background from the trash icon button */
    div[data-testid="column"]:nth-of-type(2) button {
        background: none !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin-top: -12px !important; /* Adjust vertical alignment */
        font-size: 20px !important;
        color: red !important;
        cursor: pointer;
    }

    /* Optional: subtle hover effect */
    div[data-testid="column"]:nth-of-type(2) button:hover {
        opacity: 0.7;
        transform: scale(1.1);
    }
    </style>
""", unsafe_allow_html=True)

# Logo + Header
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

# Description
st.markdown("###### 📌 Description")
st.markdown("""
**Auto Audience Generator** is a smart, LLM-powered tool designed to automatically generate targeted user audiences from natural language prompts using a structured Knowledge Graph (KG), rule-based filtering, and semantic matching.
""")
st.markdown("---")

# Load Graph
##st.cache_resource
G, matcher = build_knowledge_graph_from_config(
    "src/graph_schema.json",
    {
        "users": "data/users.csv",
        "products": "data/products.csv",
        "orders": "data/orders.csv",
        "streaming": "data/streaming.csv"
    }
), None
matcher = SemanticMatcher(G)

# Create two columns: left for label, right for trash icon
col1, col2 = st.columns([5, 1])

with col1:
    st.markdown("##### ✍️ Enter your audience description:")

with col2:
    clear_button = st.button("🗑️", key="clear_prompt", help="Clear input", use_container_width=True)

# Handle clear action
if clear_button:
    st.session_state.prompt = ""
    st.session_state.rule_conditions = None
    st.session_state.audience = set()
    st.rerun()

# Input prompt
prompt = st.text_area(label="", value=st.session_state.get("prompt", ""))
st.session_state.prompt = prompt

# Session state to persist rule & audience
if "rule_conditions" not in st.session_state:
    st.session_state.rule_conditions = None
if "audience" not in st.session_state:
    st.session_state.audience = set()

# Step 1: Extract Rule
st.markdown("---")
if st.button("🧠 Create Rule", use_container_width=True):
    with st.spinner("Extracting rule from LLM..."):
        rules_obj = extract_rules_from_prompt_llm3(prompt)
        if "error" in rules_obj:
            st.error("❌ Failed to extract rule.")
            st.code(rules_obj["raw_response"])
        else:
            st.session_state.rule_conditions = rules_obj.get("conditions", {})
            st.success("✅ Rule extracted.")

# Show Rule if available
if st.session_state.rule_conditions:
    with st.expander("🔍 Show Extracted Rule", expanded=False):
        def display_conditions(cond, indent=0):
            pad = "&nbsp;" * 4 * indent
            html = ""
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
                operator = cond.get("operator", "in")
                value = cond.get("value", cond.get("in", []))
                html += f"{pad}• <code>{field}</code> {operator} {value}<br>"
            return html
        st.markdown(display_conditions(st.session_state.rule_conditions), unsafe_allow_html=True)

# Step 2: Apply Rule
st.markdown("---")
if st.button("🎯 Generate Audience", use_container_width=True):
    with st.spinner("Filtering matched users..."):
        st.session_state.audience = apply_logical_rule(G, {"conditions": st.session_state.rule_conditions}, matcher=matcher)
        st.success(f"✅ Total Matched Users: {len(st.session_state.audience)}")

        # Sample users
        if st.session_state.audience:
            # st.markdown("### 👥 Sample Users:")
            # df = pd.DataFrame({"user_id": list(st.session_state.audience)[:10]})
            # st.dataframe(df)

            # Download CSV
            csv = pd.DataFrame({"user_id": list(st.session_state.audience)}).to_csv(index=False)
            st.download_button("📥 Download All Users as CSV",csv,file_name="audience_users.csv",key="download_csv_button")
            

# Step 3: Visualize Graph
st.markdown("---")
if st.button("🕸️ Visualize Graph", use_container_width=True):
    with st.spinner("Rendering matched user subgraph..."):
        subG = nx.DiGraph()
        for user in st.session_state.audience:
            subG.add_node(user, color='lightblue')
            for u, v, d in G.out_edges(user, data=True):
                if d.get("relation") in ["purchased", "watched"]:
                    subG.add_edge(u, v, label=d["relation"])
                    for _, tag_node, tag_data in G.out_edges(v, data=True):
                        if tag_data.get("relation") in ["tagged_as", "about"]:
                            subG.add_edge(v, tag_node, label=tag_data["relation"])

        fig, ax = plt.subplots(figsize=(7, 5))
        pos = nx.spring_layout(subG, seed=42, k=0.3)
        nx.draw(subG, pos, with_labels=True, node_color='lightgreen', edge_color='gray', node_size=500, font_size=7, ax=ax)
        edge_labels = nx.get_edge_attributes(subG, 'label')
        nx.draw_networkx_edge_labels(subG, pos, edge_labels=edge_labels, font_size=6, ax=ax)
        st.pyplot(fig)

# Footer
st.markdown("""
<hr style='border: none; border-top: 1px solid #eee;' />
<p style='text-align: center; font-size: 13px; color: gray;'>
An open-source AI toolkit by <a href="https://github.com/nik21hil" target="_blank" style="color: #888;">@nik21hil</a> · MIT Licensed
</p>
""", unsafe_allow_html=True)
