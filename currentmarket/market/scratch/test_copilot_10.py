import requests

queries = [
    ("compare", "Compare Kanakapura Road and Bagalur"),
    ("profile", "What is the absorption situation in Kanakapura Road?"),
    ("price", "What price can we command for a 3BHK in Kanakapura Road?"),
    ("absorption", "Predict absorption for 300 units in Kanakapura Road"),
    ("buyer", "Who are the primary buyers for 3BHK in South Bangalore?"),
    ("infrastructure", "What amenities are within 5km of Kanakapura Road?"),
    ("scenario", "What happens if we increase price by 500 per sqft?"),
    ("city", "Bengaluru city launches and inventory overview"),
    ("regulatory", "What are the regulatory approvals and timelines for Bagalur?"),
    ("competitor", "Who are the competitors in Bagalur?")
]

print("Testing all 10 canonical Copilot query routes...")
all_passed = True

for tag, q in queries:
    r = requests.post("http://127.0.0.1:8000/api/copilot/chat", json={"message": q})
    if r.status_code != 200:
        print(f"FAILED: {tag} ({r.status_code})")
        all_passed = False
        continue
    d = r.json()
    intent = d.get("intent")
    agents = d.get("agents_used", [])
    tools = d.get("tools_used", [])
    models = d.get("models_used", [])
    answer = d.get("answer", "")
    sources = d.get("sources", [])
    limitations = d.get("limitations", [])

    has_required_fields = all([
        intent is not None,
        isinstance(agents, list),
        isinstance(tools, list),
        isinstance(models, list),
        len(answer) > 20,
        len(sources) > 0,
        isinstance(limitations, list)
    ])

    if has_required_fields:
        print(f"  [PASS] {tag.upper():<15} Intent: {intent:<25} Agents: {len(agents)} Tools: {len(tools)} Models: {len(models)}")
    else:
        print(f"  [FAIL] {tag.upper():<15} Missing fields!")
        all_passed = False

if all_passed:
    print("\nALL 10 COPILOT QUERY TYPES PASSED WITH STANDARDIZED CONTRACT!")
else:
    print("\nSOME COPILOT QUERIES FAILED.")
