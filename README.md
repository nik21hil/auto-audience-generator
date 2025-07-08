# 🧠 Auto Audience Generator

> The **Auto Audience Generator** is a smart, LLM-powered tool designed to automatically generate targeted user audiences from natural language prompts using a structured **Knowledge Graph (KG)**, rule-based filtering, and semantic matching.

[![Streamlit App](https://img.shields.io/badge/Live_App-Click_to_Launch-00bfff?logo=streamlit)](https://auto-audience-generator-22sdvxi3phzzen5a4bulnw.streamlit.app/) | ![License](https://img.shields.io/badge/license-MIT-green)

---

## ✨ Overview

This tool allows marketers, analysts, and product teams to:

- Input natural-language prompts like:  
  _"Find crypto enthusiasts"_  
  _"Show users interested in fitness and wellness"_  
  _"Find near graduting studnets"_

- Behind the scenes, it:
  1. **Builds a Knowledge Graph** using user-product-content interaction data.
  2. **Uses LLM to extract logical audience filtering rules** (e.g., age > 18, tag IN [“crypto”, “blockchain”]).
  3. **Expands matching fields** using semantic embeddings for robust keyword-to-field-value matching.
  4. **Applies rules on the KG** and outputs the list of matched users.
  5. **Visualizes user-item relationships** using a dynamic subgraph display.

---

## ⚙️ Key Components

| Module               | Description                                                               |
|--------------------|-----------------------------------------------------------------------------|
| graph_builder.py   | Constructs the Knowledge Graph from CSVs based on a JSON schema             |
| prompt_to_rules.py | Uses OpenRouter + LLM to turn prompts into executable logical rules         |
| graph_queries.py   | Evaluates logical rules (AND/OR/nested) on the KG to select audience        |
| semantic_matcher.py| Uses embedding similarity to expand keywords like "crypto" → "blockchain"   |
| app.py             | Streamlit interface to run everything in one click                          |

---

## ✅ Current Capabilities

- [x] Multi-source Knowledge Graph with user/product/content data
- [x] Natural language → LLM-based rules (AND, OR, nested)
- [x] Embedding-based synonym matching (e.g., “crypto” → “blockchain”)
- [x] Graph subvisualization of user-to-interest relationships
- [x] Streamlit UI to demo everything end-to-end

---

## 📊 Sample Data Overview

| Dataset       | Description                              |
| ------------- | ---------------------------------------- |
| users.csv     | User demographics: age, gender, location |
| products.csv  | Product info with tags/categories        |
| orders.csv    | User-product purchase history            |
| streaming.csv | User-content interaction & genres        |

---

## 📁 Folder Structure

```
auto-audience-generator/
├── assets/            # To store logo images or any other artifact
├── data/              # Sample CSVs
├── notebooks/         # Jupyter demo notebooks
├── src/               # Modular Python code
│   ├── graph_builder.py # Knowledge Graph builder
│   ├── graph_queries.py # Rule execution engine
│   ├── prompt_to_rules.py # LLM-based rule extractor
│   ├── semantic_matcher.py # Embedding-based semantic expander
├── app.py             # Main Streamlit app
├── requirements.txt
│── README.md
```

---

## 🛠️ Setup Instructions
- **Clone the repo**:
  - git clone https://github.com/nik21hil/auto-audience-generator.git
  - cd auto-audience-generator
- **(Optional) Create virtual environment**:
  - python3 -m venv venv
  - source venv/bin/activate
- **Install dependencies**:
  - pip install -r requirements.txt
- **Add your OpenRouter API Key (in .streamlit/secrets.toml)**:
  - OPENROUTER_API_KEY = "your-key-here"
- **Run the Streamlit app**:
  - streamlit run app.py

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

## 🧾 License

MIT License — feel free to fork, remix, and use.

---

## 🙌 Acknowledgements

Built by [@nik21hil](https://github.com/nik21hil)  

---

## 📬 Feedback
For issues or suggestions, feel free to open a [GitHub issue](https://github.com/nik21hil/auto-audience-generator/issues) or connect via [LinkedIn](https://linkedin.com/in/nkhlsngh).

---

Enjoy building! 🎯


