import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

import streamlit as st
import json
import networkx as nx
import matplotlib.pyplot as plt

from graph_builder import build_knowledge_graph_from_config
from graph_queries import apply_logical_rule
from prompt_to_rules import extract_rules_from_prompt_llm3
from semantic_matcher import SemanticMatcher

# Streamlit config
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

st.markdown("###### 📌 Description")
st.markdown("""
**Auto Audience Generator** is a smart, LLM-powered tool designed to automatically generate targeted user audiences from natural language prompts using a structured Knowledge Graph (KG), rule-based filtering, and semantic matching.
""")

st.markdown("---")

st.cache_resource
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

if st.button("🔄 Refresh Graph Cache"):
    load_graph_and_matcher.clear()
    st.experimental_rerun()

st.markdown("#### 🛠 Debugging Info")

# Show one user node and its attributes
for node, data in G.nodes(data=True):
    if data.get("type") == "user":
        st.write("👤 Sample User Node:", node)
        st.write("📋 Attributes:", data)
        break

st.markdown("###### ✍️ Enter your audience description:")
prompt = st.text_area(label="", value="Find crypto enthusiasts")

if st.button("Generate Audience"):
    try:
        rules_obj = extract_rules_from_prompt_llm3(prompt)

        if "error" in rules_obj:
            st.error("❌ LLM failed to return clean JSON.")
            st.code(rules_obj["raw_response"])
            st.stop()

        conditions = rules_obj.get("conditions", {})
        if not conditions:
            st.warning("No rule found.")
            st.stop()

        # Recursive display function

        def display_conditions(cond, indent=0):
            html = ""
            pad = "&nbsp;" * 4 * indent
        
            # If it's a single-item AND/OR, unwrap it
            if "and" in cond and len(cond["and"]) == 1:
                return display_conditions(cond["and"][0], indent)
            if "or" in cond and len(cond["or"]) == 1:
                return display_conditions(cond["or"][0], indent)
        
            if "and" in cond:
                html += f"{pad}<span style='font-size:13px;'><b>AND</b></span><br>"
                for c in cond["and"]:
                    html += display_conditions(c, indent + 1)
            elif "or" in cond:
                html += f"{pad}<span style='font-size:13px;'><b>OR</b></span><br>"
                for c in cond["or"]:
                    html += display_conditions(c, indent + 1)
            else:
                field = cond.get("field", "")
                values = cond.get("in", [])
                operator = cond.get("operator", "in")
                value = cond.get("value", None)
        
                if operator == "in":
                    html += f"{pad}<span style='font-size:13px;'>&#8226; <code>{field}</code> in {values}</span><br>"
                else:
                    html += f"{pad}<span style='font-size:13px;'>&#8226; <code>{field}</code> {operator} {value}</span><br>"
        
            return html

        
        with st.expander("🔍 Show Extracted Rule", expanded=False):
            html = display_conditions(conditions)
            st.markdown(html, unsafe_allow_html=True)

        st.markdown("##### 🎯 Final Audience")
        audience = apply_logical_rule(G, {"conditions": conditions}, matcher=matcher)
        st.success(f"Matched Users ({len(audience)}): {sorted(audience)}")

        subG = nx.DiGraph()
        for user in audience:
            subG.add_node(user, color='lightblue')
            for u, v, d in G.out_edges(user, data=True):
                if d.get("relation") in ["purchased", "watched"]:
                    subG.add_edge(u, v, label=d["relation"])
                    for _, tag_node, tag_data in G.out_edges(v, data=True):
                        if tag_data.get("relation") in ["tagged_as", "about"]:
                            subG.add_edge(v, tag_node, label=tag_data["relation"])

        fig, ax = plt.subplots(figsize=(5, 3))
        pos = nx.spring_layout(subG)
        nx.draw(subG, pos, with_labels=True, node_color='lightgreen', edge_color='gray', node_size=500, ax=ax)
        edge_labels = nx.get_edge_attributes(subG, 'label')
        nx.draw_networkx_edge_labels(subG, pos, edge_labels=edge_labels, ax=ax)
        st.pyplot(fig)

    except Exception as e:
        st.error(f"❌ Failed to generate audience: {str(e)}")

st.markdown("""
<hr style='border: none; border-top: 1px solid #eee;' />
<p style='text-align: center; font-size: 13px; color: gray;'>
An open-source AI toolkit by <a href="https://github.com/nik21hil" target="_blank" style="color: #888;">@nik21hil</a> · MIT Licensed
</p>
""", unsafe_allow_html=True)
