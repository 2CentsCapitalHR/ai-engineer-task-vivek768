import json

def load_checklist(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

def check_aoa(uploaded_headings, aoa_type, checklist):
    required = checklist[aoa_type]
    missing = {}
    extra = []

    for part, clauses in required.items():
        miss = [c for c in clauses if c not in uploaded_headings]
        if miss:
            missing[part] = miss

    for clause in uploaded_headings:
        if not any(clause in c for clauses in required.values() for c in clauses):
            extra.append(clause)

    match_pct = round(100 * (1 - sum(len(m) for m in missing.values()) / sum(len(v) for v in required.values())), 2)

    return {"missing": missing, "extra": extra, "match_percentage": match_pct}
