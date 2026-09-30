import sys
import os

sys.path.insert(0, os.getcwd())
# Ensure UTF-8 output encoding for Windows stdout
sys.stdout.reconfigure(encoding='utf-8')

from backend.copilot.llm_orchestrator import get_llm_orchestrator

test_queries = [
    "why not whitefield?",
    "What is the historical absorption in Whitefield?",
    "What are the verified projects in Whitefield?",
    "What is the predicted price for a 2BHK Mid project in Whitefield?",
    "Compare Whitefield and Kanakapura Road.",
    "What buyer segments are relevant for Whitefield?",
    "Should I launch a 300-unit 3BHK project in Whitefield at ₹6500/sqft?",
    "What is the historical buyer profile for 3BHK?",
    "What infrastructure exists within 5km of Whitefield?",
    "What happens if I increase the project from 200 to 500 units?"
]

def run_tests():
    orch = get_llm_orchestrator()
    passed = 0
    total = len(test_queries)

    results = []

    for idx, q in enumerate(test_queries, 1):
        print(f"\n==================================================")
        print(f"TEST {idx}/{total}: {q}")
        print(f"==================================================")
        try:
            res = orch.process_query(q)
            status = res.get("status")
            intent = res.get("intent")
            agents = res.get("agents_used", [])
            tools = res.get("tools_used", [])
            evidence = res.get("evidence", [])
            answer = res.get("answer", "")

            print(f"Status: {status}")
            print(f"Intent: {intent}")
            print(f"Agents Used: {agents}")
            print(f"Tools Used: {tools}")
            print(f"Evidence Payloads: {len(evidence)}")
            print(f"Answer Word Count: {len(answer.split())}")
            print(f"Answer Snippet:\n{answer[:300]}...\n")

            # Validation criteria for Stage 1 & Stage 2 success
            is_valid = (
                status == "success" and
                len(tools) > 0 and
                len(evidence) > 0 and
                len(answer.strip()) > 30
            )

            if is_valid:
                passed += 1
                print(f"RESULT: PASS")
            else:
                print(f"RESULT: FAIL (Validation check failed)")

            results.append({
                "query": q,
                "status": status,
                "intent": intent,
                "agents": agents,
                "tools": tools,
                "evidence_count": len(evidence),
                "answer_word_count": len(answer.split()),
                "passed": is_valid
            })
        except Exception as e:
            print(f"RESULT: ERROR - {e}")
            results.append({
                "query": q,
                "error": str(e),
                "passed": False
            })

    print(f"\n==================================================")
    print(f"COPILOT TEST SUMMARY: {passed}/{total} PASSED")
    print(f"==================================================")
    return results

if __name__ == "__main__":
    run_tests()
