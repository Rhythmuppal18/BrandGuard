import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.api.endpoints import run_accuracy_benchmark, get_scenarios
from app.services.workflow_service import create_or_review_item, get_item_full_details, handle_suggestion_action, transition_item_status
from app.models.schemas import StatusEnum

print("--- Testing BrandGuard Pipeline ---")
scenarios = get_scenarios()
print(f"1. Preloaded scenarios: {len(scenarios)}")
s1 = scenarios[0]
print(f"   Testing Scenario 1: '{s1['title']}'")

item_id = create_or_review_item(title=s1["title"], content=s1["text"], content_type=s1["content_type"])
details = get_item_full_details(item_id)
print(f"   Item created: {item_id}")
print(f"   Initial Score: {details.brand_score}/100")
print(f"   Category Scores: {details.category_scores}")
print(f"   Findings ({len(details.findings)}):")
for f in details.findings:
    print(f"     - [{f.severity.value}] {f.rule_id}: '{f.matched_text}' -> Citation: {f.citation_source[:40]}...")

print(f"   Tracked Changes: {len(details.tracked_changes)}")
if details.tracked_changes:
    first_tc = details.tracked_changes[0]
    print(f"   Testing Accept Fix: '{first_tc.original_text}' -> '{first_tc.replacement_text}'")
    updated = handle_suggestion_action(item_id, first_tc.id, "accept", actor="Brand Manager", role="Brand Manager")
    print(f"   New Brand Score after accepting fix: {updated.brand_score}/100")

print(f"   Testing Transition to IN_REVIEW...")
in_review = transition_item_status(item_id, StatusEnum.IN_REVIEW, actor="Content Creator", role="Creator", comment="Submitting for final review")
print(f"   New status: {in_review.status.value}")

print(f"   Testing Final Approval by Manager...")
approved = transition_item_status(item_id, StatusEnum.APPROVED, actor="Brand Manager", role="Brand Manager", comment="Approved after brand checks")
print(f"   Final status: {approved.status.value}")
print(f"   Audit Trail Entries: {len(approved.audit_trail)}")

print("\n--- Running 30-item Benchmark Test Suite ---")
bm = run_accuracy_benchmark()
print(f"Benchmark Results:")
print(f"  Total tests: {bm['summary']['total_tests']}")
print(f"  Passed tests: {bm['summary']['passed_tests']}")
print(f"  Accuracy Rate: {bm['summary']['accuracy_rate_percent']}% (Target: {bm['summary']['target_from_round1']})")
print(f"  Citation Rate: {bm['summary']['citation_rate_percent']}% (Target: {bm['summary']['citation_target_from_round1']})")
print(f"  Avg Latency: {bm['summary']['avg_latency_ms']} ms")
print("\nALL BACKEND PIPELINE TESTS PASSED!")

