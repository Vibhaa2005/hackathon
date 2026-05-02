import os
from typing import List, Dict


def _groq_generate(prompt: str) -> str:
    from groq import Groq
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=1024,
    )
    return response.choices[0].message.content.strip()


def _fallback_rationale(query: str, standard: Dict) -> str:
    return (
        f"{standard['standard_number']} ({standard['title']}) applies to your product "
        f"because it falls under the '{standard['category']}' category. "
        f"Scope: {standard.get('scope', 'See standard for full scope.')}"
    )


def generate_rationale(query: str, standards: List[Dict]) -> str:
    standards_text = ""
    for i, s in enumerate(standards, 1):
        standards_text += (
            f"\n{i}. {s['standard_number']} — {s['title']}\n"
            f"   Category: {s['category']}\n"
            f"   Description: {s['description'][:200]}...\n"
        )

    prompt = f"""You are an expert in Bureau of Indian Standards (BIS) for Building Materials.

A user describes their product or query as:
\"{query}\"

The following BIS standards have been retrieved as most relevant:
{standards_text}

For each standard, provide:
1. A concise 1-2 sentence rationale explaining WHY this standard applies to the given product/query.
2. The key compliance requirement most relevant to this product.

Respond in this exact JSON format:
[
  {{
    "standard_number": "IS XXX:YYYY",
    "rationale": "...",
    "key_requirement": "..."
  }}
]

Only respond with valid JSON, no extra text."""

    groq_key = os.environ.get("GROQ_API_KEY", "")
    if groq_key:
        try:
            return _groq_generate(prompt)
        except Exception:
            pass

    # Rule-based fallback
    result = []
    for s in standards:
        result.append({
            "standard_number": s["standard_number"],
            "rationale": _fallback_rationale(query, s),
            "key_requirement": s.get("key_requirements", ["See standard for details."])[0],
        })
    import json
    return json.dumps(result)
