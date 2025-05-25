import openai
import json
import json5
import re
import os
import requests
#from .utils import clean_json_response

# openai.api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")

openai.api_key = os.getenv("OPENROUTER_API_KEY")
openai.api_base = "https://openrouter.ai/api/v1"


def clean_json_response(raw_text):
    # Normalize smart quotes
    raw_text = raw_text.replace("“", "\"").replace("”", "\"").replace("‘", "'").replace("’", "'")

    # Remove markdown/code fences
    raw_text = re.sub(r"```.*?\n|```", "", raw_text).strip()

    # Remove trailing commas before closing braces/brackets
    raw_text = re.sub(r",\s*([}\]])", r"\1", raw_text)

    # Track outermost JSON object
    open_braces = 0
    close_index = None
    for i, char in enumerate(raw_text):
        if char == "{":
            open_braces += 1
        elif char == "}":
            open_braces -= 1
            if open_braces == 0:
                close_index = i
                break

    if close_index is not None:
        raw_text = raw_text[:close_index + 1]

    return raw_text


def extract_rules_from_prompt_llm(prompt):
    system_msg = """
You are an intelligent assistant that extracts targeting rules for audience segmentation.
Given a user query in natural language, return a JSON object with two keys:
- "demographics": with possible keys like "age", "location", etc.
- "interests": a list of interests (e.g., sports, AI, yoga, etc.)

Return JSON only. No explanation or markdown.
"""

    response = openai.ChatCompletion.create(
        model="mistralai/mixtral-8x7b-instruct",
        messages=[
            {"role": "system", "content": system_msg.strip()},
            {"role": "user", "content": prompt.strip()}
        ],
        temperature=0.2
    )

    try:
        reply = response["choices"][0]["message"]["content"]
        return json.loads(reply)
    except Exception as e:
        print("❌ Failed to parse response:", e)
        print("Raw content:", reply)
        return {}

def extract_rules_from_prompt_llm2(prompt):
    system_msg = """
You are an intelligent assistant that creates user persona filters for audience segmentation.

Given a natural language query like "users about to graduate" or "retired people in Florida",
return a JSON object with a single top-level key: "persona"

The value of "persona" is an object that can contain any of these:
- "age": { "operator": ">", "<", or "=" , "value": number }
- "location": string or list of strings
- "education_level": string
- "tag": list of product tags (e.g., ["blockchain", "career", "fitness"])
- "genre": list of content genres (e.g., ["sports", "self-help", "comedy"])
- "gender": string
- etc.

Choose only the fields relevant to the intent.
Example output for "users about to graduate":

{
  "persona": {
    "age": { "operator": ">", "value": 20 },
    "education_level": "College Senior",
    "tag": ["job prep", "career"],
    "genre": ["technology"]
  }
}

Return valid JSON only. Do not use markdown or explanations.
"""

    response = openai.ChatCompletion.create(
        model="mistralai/mixtral-8x7b-instruct",
        messages=[
            {"role": "system", "content": system_msg.strip()},
            {"role": "user", "content": prompt.strip()}
        ],
        temperature=0.2,
        max_tokens=512  # ← added!
    )

    try:
        reply = response["choices"][0]["message"]["content"]
        cleaned = clean_json_response(reply)
        return json.loads(cleaned)
    except Exception as e:
        print("❌ Failed to parse response:", e)
        print("Raw content:", reply)
        return {}

def extract_rules_from_prompt_llm3_old(prompt):
    system_msg = """
You are an intelligent assistant that creates audience filtering rules based on user data stored in a Knowledge Graph.

The graph includes users, products, and content nodes with these available fields:

- user.age → number
- user.gender → string
- user.location → string
- product.tag → list of tags (used as user interests)
- product.category → list of categories (optional)
- content.genre → list of genres (used as user interests)

Please use only these fields in your rule generation:
- age, gender, location, tag, genre

Return up to 3 rule strategies like this:

{
  "rules": [
    {
      "name": "Some audience",
      "conditions": {
        "and": [
          { "field": "age", "operator": ">", "value": 20 },
          {
            "or": [
              { "field": "tag", "in": ["crypto", "blockchain"] },
              { "field": "genre", "in": ["finance", "tech"] }
            ]
          }
        ]
      }
    }
  ]
}

Do not use fields like investment_activity, education_level, social_media, etc.  
Return only valid JSON - no markdown or explanations.

"""

    response = openai.ChatCompletion.create(
        model="mistralai/mixtral-8x7b-instruct",
        messages=[
            {"role": "system", "content": system_msg.strip()},
            {"role": "user", "content": prompt.strip()}
        ],
        temperature=0.2,
        max_tokens=512  # ← added!
    )

    try:
        reply = response["choices"][0]["message"]["content"]
        cleaned = clean_json_response(reply)
        return json.loads(cleaned)
    except Exception as e:
        print("❌ Failed to parse response:", e)
        print("Raw content:", reply)
        return {}


def extract_rules_from_prompt_llm3_multiplerules(prompt, verbose=False):
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return {
            "error": "Missing OPENROUTER_API_KEY in environment.",
            "raw_response": None
        }

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    system_msg = """
You are an intelligent assistant that creates audience filtering rules based on user data stored in a Knowledge Graph.

The graph includes users, products, and content nodes with these available fields:
- user.age → number
- user.gender → string
- user.location → string
- product.tag → list of tags (used as user interests)
- product.category → list of categories (optional)
- content.genre → list of genres (used as user interests)

Only use these fields: age, gender, location, tag, genre

Return JSON like:
{
  "rules": [
    {
      "name": "Crypto Enthusiasts",
      "conditions": {
        "or": [
          { "field": "tag", "in": ["crypto", "blockchain"] },
          { "field": "genre", "in": ["finance"] }
        ]
      }
    }
  ]
}
Return only valid JSON — no markdown, no explanation.
""".strip()

    payload = {
        "model": "mistralai/mixtral-8x7b-instruct",
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt.strip()}
        ],
        "temperature": 0.3
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        response_data = response.json()

        raw = response_data["choices"][0]["message"]["content"]
        cleaned = clean_json_response(raw)

        if verbose:
            print("🧠 Raw LLM Output:", raw)
            print("🧹 Cleaned JSON:", cleaned)

        return json5.loads(cleaned)

    except Exception as e:
        return {
            "error": str(e),
            "raw_response": response.text if 'response' in locals() else "No response"
        }

def extract_rules_from_prompt_llm3(prompt, verbose=True):
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return {
            "error": "Missing OPENROUTER_API_KEY in environment.",
            "raw_response": None
        }

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    system_msg = """
You are an intelligent assistant that generates a single, structured audience filtering rule using data from a Knowledge Graph.

The graph includes users, products, and content nodes with the following fields:
- user.age → number
- user.gender → string
- user.location → string
- product.tag → list of tags (used as user interests)
- content.genre → list of genres (used as user interests)

Instructions:
- Generate one audience rule using only the following fields: age, gender, location, tag, genre.
- Do not invent or include any other fields like content, education_level, occupation, job_title, etc.
- The rule must have a top-level key: "conditions".
- Combine conditions using logical operators "and" and "or", supporting nested structures such as:
  - { "and": [ ... ] }
  - { "or": [ ... ] }
  - { "and": [ ..., { "or": [ ... ] } ] }

Additional guidance:
- If the prompt implies abstract traits (e.g., "crypto fans", "sports lovers", "users about to graduate"), map these to relevant tag or genre values based on the prompt intent.
- For numeric fields like age, use standard operators like ">", "<", ">=", "<=", "=".
- If an age range is implied (e.g., "young adults", "about to retire"), return both lower and upper bound conditions inside an "and" block.
- Avoid unnecessary use of "and"/"or" wrappers when there is only one condition.

Output Format:
Return only valid JSON structured like:
{
  "conditions": {
    ...
  }
}

Return only the JSON object — no markdown, no explanation.
"""

    payload = {
        "model": "mistralai/mixtral-8x7b-instruct",
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt.strip()}
        ],
        "temperature": 0.3
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        response_data = response.json()

        raw = response_data["choices"][0]["message"]["content"]
        cleaned = clean_json_response(raw)

        if verbose:
            print("🧠 Raw LLM Output:", raw)
            print("🧹 Cleaned JSON:", cleaned)

        return json5.loads(cleaned)

    except Exception as e:
        return {
            "error": str(e),
            "raw_response": response.text if 'response' in locals() else "No response"
        }
