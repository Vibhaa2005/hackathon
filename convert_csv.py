"""
One-time script: converts indian_standards_dataset.csv → data/bis_standards.json
"""
import csv
import json
import os
import re
import sys

CSV_PATH = os.path.join(os.path.dirname(__file__), "data", "indian_standards_dataset.csv")
OUT_PATH = os.path.join(os.path.dirname(__file__), "data", "bis_standards.json")


def clean(text: str) -> str:
    """Remove junk characters and normalise whitespace."""
    if not text:
        return ""
    # Replace common garbled unicode sequences
    text = text.replace("â", "'").replace("Ã", "x").replace("Â", "").replace("â", "-")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_key_requirements(raw: str) -> list[str]:
    """Split pipe-delimited key_requirements into a clean list."""
    if not raw:
        return []
    parts = [clean(p) for p in raw.split("|")]
    parts = [p for p in parts if len(p) > 8]          # drop trivial fragments
    parts = [re.sub(r"^[\d\.\s]+", "", p).strip() for p in parts]  # strip leading numbers
    parts = [p for p in parts if p and not p.startswith("table:") and "table:" not in p.lower()[:20]]
    return parts[:8]                                   # keep at most 8 requirements


def make_id(section: str, idx: int) -> str:
    abbr = {
        "Cement and Concrete": "CC",
        "Building Limes": "BL",
        "Stones": "ST",
        "Wood Products for Building": "WP",
        "Wood Products": "WP",
        "Gypsum Building Materials": "GB",
        "Timber": "TM",
        "Bitumen and Tar Products": "BT",
        "Floor, Wall, Roof Coverings and Finishes": "FR",
        "Water Proofing and Damp Proofing Materials": "WD",
        "Sanitary Appliances and Water Fittings": "SW",
        "Structural Steels": "SS",
        "Light Metal and Their Alloys": "LM",
        "Structural Shapes": "SH",
        "Welding Electrodes and Wires": "WE",
        "Threaded Fasteners and Rivets": "TF",
        "Wire Ropes and Wire Products": "WR",
        "Glass": "GL",
        "Fillers, Stoppers and Putties": "FS",
        "Thermal Insulation Materials": "TI",
        "Plastics": "PL",
        "Conductors and Cables": "CB",
        "Wiring Accessories": "WA",
        "Builder's Hardware": "BH",
        "Doors, Windows and Shutters": "DW",
        "Concrete Reinforcement": "CR",
    }
    code = abbr.get(section.strip(), "BIS")
    return f"{code}_{idx:04d}"


def infer_keywords(title: str, section: str, scope: str) -> list[str]:
    words = set()
    for src in [title, section, scope[:200]]:
        for w in re.split(r"[\s,;/\-\(\)]+", src.lower()):
            w = w.strip(".")
            if len(w) > 3 and not w.isdigit():
                words.add(w)
    return sorted(words)[:20]


def main():
    standards = []
    seen_ids = set()
    idx = 1

    with open(CSV_PATH, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            is_number  = clean(row.get("is_number", ""))
            year_raw   = row.get("year", "").strip()
            title      = clean(row.get("title", ""))
            revision   = clean(row.get("revision", ""))
            section    = clean(row.get("section", ""))
            scope      = clean(row.get("scope", ""))
            key_reqs   = parse_key_requirements(row.get("key_requirements", ""))
            reference  = clean(row.get("reference", ""))

            if not is_number or not title:
                continue

            # Normalise standard number: "IS 383 : 1970" → "IS 383:1970"
            std_num = re.sub(r"\s*:\s*", ":", is_number).strip()

            # De-duplicate
            if std_num in seen_ids:
                continue
            seen_ids.add(std_num)

            try:
                year = int(year_raw)
            except ValueError:
                year = None

            description = scope[:300].rstrip(",;")
            if revision:
                description = f"{description} ({revision})" if description else revision

            uid = make_id(section, idx)
            idx += 1

            # Embedding text — rich concatenation for better retrieval
            text_parts = [std_num, title, section, scope, " ".join(key_reqs)]
            emb_text = " | ".join(filter(None, text_parts))

            standards.append({
                "id":                 uid,
                "standard_number":    std_num,
                "title":              title,
                "category":           section,
                "description":        description,
                "scope":              scope,
                "key_requirements":   key_reqs,
                "applicable_products": [],
                "year":               year,
                "keywords":           infer_keywords(title, section, scope),
                "text":               emb_text,
            })

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(standards, f, ensure_ascii=False, indent=2)

    print(f"Written {len(standards)} standards -> {OUT_PATH}")


if __name__ == "__main__":
    main()
