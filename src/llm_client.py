import json
import os
from typing import List, Dict


DATABRICKS_HOST = "https://dbc-3f37515c-6bbb.cloud.databricks.com"
LLM_ENDPOINT    = "databricks-meta-llama-3-1-8b-instruct"


def _get_client():
    from openai import OpenAI
    token = os.environ.get("DATABRICKS_TOKEN", "")
    if not token:
        return None
    return OpenAI(
        api_key=token,
        base_url=f"{DATABRICKS_HOST}/serving-endpoints",
    )


def _fallback_rationale(query: str, standard: Dict) -> Dict:
    return {
        "standard_number": standard["standard_number"],
        "rationale": (
            f"{standard['standard_number']} ({standard['title']}) applies to your product "
            f"because it falls under the '{standard['category']}' category. "
            f"Scope: {standard.get('scope', 'See standard for full scope.')}"
        ),
        "key_requirement": standard.get("key_requirements", ["See standard for details."])[0],
    }


def generate_rationale(query: str, standards: List[Dict]) -> str:
    standards_text = ""
    for i, s in enumerate(standards, 1):
        standards_text += (
            f"\n{i}. {s['standard_number']} — {s['title']}\n"
            f"   Category: {s['category']}\n"
            f"   Scope: {s.get('scope', '')[:200]}\n"
        )

    prompt = f"""You are an expert in Bureau of Indian Standards (BIS) for Building Materials.

A user describes their product or query as:
"{query}"

The following BIS standards have been retrieved as most relevant:
{standards_text}

For each standard, provide:
1. A concise 1-2 sentence rationale explaining WHY this standard applies to the given product/query.
2. The single most relevant key compliance requirement for this product.

Respond in this exact JSON format and nothing else:
[
  {{
    "standard_number": "IS XXX:YYYY",
    "rationale": "...",
    "key_requirement": "..."
  }}
]"""

    client = _get_client()
    if client:
        try:
            response = client.chat.completions.create(
                model=LLM_ENDPOINT,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1024,
            )
            return response.choices[0].message.content.strip()
        except Exception:
            pass

    # Rule-based fallback when no token is available
    result = [_fallback_rationale(query, s) for s in standards]
    return json.dumps(result)
