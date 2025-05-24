# 🧠 Auto Audience Generator

The **Auto Audience Generator** is a smart, LLM-powered tool designed to automatically generate targeted user audiences from natural language prompts using a structured **Knowledge Graph (KG)**, rule-based filtering, and semantic matching.

---

## 🚀 What It Does

This tool allows marketers, analysts, and product teams to:

- Input natural-language prompts like:  
  _"Find crypto enthusiasts"_  
  _"Show users interested in fitness and wellness"_  
  _"Target Gen Z males in California who like gaming"_

- Behind the scenes, it:
  1. **Builds a Knowledge Graph** using user-product-content interaction data.
  2. **Uses LLM to extract logical audience filtering rules** (e.g., age > 18, tag IN [“crypto”, “blockchain”]).
  3. **Expands matching fields** using semantic embeddings for robust keyword-to-field-value matching.
  4. **Applies rules on the KG** and outputs the list of matched users.
  5. **Visualizes user-item relationships** using a dynamic subgraph display.

---

## ⚙️ Key Components

| Module               | Description                                                                 |
|----------------------|-----------------------------------------------------------------------------|
| `graph_builder.py`   | Constructs the Knowledge Graph from CSVs based on a JSON schema             |
| `prompt_to_rules.py` | Uses OpenRouter + LLM to turn prompts into executable logical rules         |
| `graph_queries.py`   | Evaluates logical rules (AND/OR/nested) on the KG to select audience        |
| `semantic_matcher.py`| Uses embedding similarity to expand keywords like "crypto" → "blockchain"   |
| `app.py`             | Streamlit interface to run everything in one click                          |

---

## 🖥️ Streamlit Interface

The app provides a clean and interactive web interface where you can:

- Type any audience request as prompt  
- Click `Generate Audience`  
- View matched users, extracted rules (collapsible), and graph visualizations  

---

## 📦 Sample Prompt Examples

| Prompt                                | What It Does                                                |
|---------------------------------------|-------------------------------------------------------------|
| `Find crypto enthusiasts`             | Finds users with related interests like crypto/blockchain   |
| `Show Gen Z gamers in California`     | Filters by age, location, and interest                      |
| `Fitness & wellness fans over 40`     | Applies nested AND/OR rules across fields                   |

---

## ✅ Current Capabilities

- [x] Multi-source Knowledge Graph with user/product/content data
- [x] Natural language → LLM-based rules (AND, OR, nested)
- [x] Embedding-based synonym matching (e.g., “crypto” → “blockchain”)
- [x] Graph subvisualization of user-to-interest relationships
- [x] Streamlit UI to demo everything end-to-end

---

## 🛠️ Planned Enhancements

| Category              | Planned Feature                                                                 |
|------------------------|----------------------------------------------------------------------------------|
| 🔄 Rule Intelligence   | Score each rule with confidence / prompt follow-ups to relax or tighten rules   |
| ✍️ Rule Editor         | In-app manual rule editing + live rule preview                                  |
| 💾 Rule History        | Save, re-use, and manage frequently used prompts and rules                      |
| 🧠 Smarter Matching     | Expand KG and embeddings to support domain-specific synonyms                    |
| 🧩 Auto Schema Build   | Ingest raw CSV + data dictionary → auto-create graph schema                     |
| ⚡ UX Improvements     | Tag clouds, field highlights, advanced visualizations                           |

---

## 📁 Project Structure

