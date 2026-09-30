import sys
import os

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from backend.copilot.copilot_service import get_copilot_service

def test_query(q, history=None):
    svc = get_copilot_service()
    print("=" * 70)
    print(f"QUERY: {q}")
    print("=" * 70)
    res = svc.chat(q, history or [])
    print(f"STATUS: {res.get('status')}")
    print(f"INTENT: {res.get('intent')}")
    print(f"AGENTS USED: {res.get('agents_used')}")
    print(f"TOOLS USED: {res.get('tools_used')}")
    print(f"MODELS USED: {res.get('models_used')}")
    print(f"EVIDENCE COUNT: {len(res.get('evidence', []))}")
    print(f"SOURCES: {res.get('sources')}")
    print("ANSWER PREVIEW:")
    ans = res.get('answer', '')
    print(ans[:500] + ("..." if len(ans) > 500 else ""))
    print("\n")
    return res

if __name__ == "__main__":
    print("STARTING COPILOT BENCHMARK VERIFICATION SUITE\n")
    # 1. Historical buyer demographics for 3BHK
    r1 = test_query("Historical buyer demographics for 3BHK")

    # 2. Who are the historical buyers for 3BHK?
    r2 = test_query("Who are the historical buyers for 3BHK?")

    # 3. What buyer segments prefer 3BHK?
    r3 = test_query("What buyer segments prefer 3BHK?")

    # 4. What is the predicted launch price for a 2BHK mid-segment project in Bagalur?
    r4 = test_query("What is the predicted launch price for a 2BHK mid-segment project in Bagalur?")

    # 5. How does raising units from 200 to 500 affect absorption in Kanakapura Road?
    r5 = test_query("How does raising units from 200 to 500 affect absorption in Kanakapura Road?")

    # 6. Context independence check: follow up scenario question immediately with buyer question in history
    hist = [
        {"role": "user", "content": "How does raising units from 200 to 500 affect absorption in Kanakapura Road?"},
        {"role": "assistant", "content": r5.get("answer", "")}
    ]
    print("\n>>> TESTING CONTEXT INDEPENDENCE AFTER SCENARIO QUESTION >>>")
    r6 = test_query("Who are the historical buyers for 3BHK?", history=hist)

