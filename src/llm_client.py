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
            f"\n{i}. {s['standard_number']} — {s['title']} [{s['category']}]"
            f" | {s.get('scope', '')[:100]}\n"
        )

    prompt = f"""BIS expert. Product: "{query}"

Standards:
{standards_text}
For each, give a 1-sentence rationale and top compliance requirement.
JSON only:
[{{"standard_number":"IS X:Y","rationale":"...","key_requirement":"..."}}]"""

    client = _get_client()
    if client:
        try:
            response = client.chat.completions.create(
                model=LLM_ENDPOINT,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=512,
            )
            return response.choices[0].message.content.strip()
        except Exception:
            pass

    # Rule-based fallback when no token is available
    result = [_fallback_rationale(query, s) for s in standards]
    return json.dumps(result)
