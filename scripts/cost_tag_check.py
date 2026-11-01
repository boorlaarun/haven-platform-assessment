"""
B2, part 2 — implement the cost-tagging check.

Read fixtures/plan.json for the shape of a `terraform show -json` plan: a `resource_changes`
list, where each entry has a `type`, an `address`, and `change.after.tags`.

Implement check_plan() so it:
  - Looks at every resource being created or changed (skip anything not in
    change.actions, e.g. a pure "no-op" / "read" change).
  - Fails (returns a non-zero exit code) if the resource is missing the tag that identifies
    the real billing unit, per README.md's domain model — not whatever tag the resource
    happens to already carry.
  - Is idempotent: running this twice against the same plan file produces the same result,
    with no duplicate output and no flipped pass/fail.
  - Prints which specific resource address(es) are missing the tag.

Run manually: python scripts/cost_tag_check.py fixtures/plan.json
"""
import json
import sys

REQUIRED_TAG = "landlord_account_id"


def check_plan(plan_path: str) -> int:
    """
    Returns an exit code: 0 if every taggable resource being created/changed has
    `landlord_account_id`, non-zero otherwise.
    """
    with open(plan_path) as f:
        plan = json.load(f)

    # Idempotency key = resource address. A set removes duplicates and
    # sorted() below fixes the output order, so reruns give identical output.
    missing = set()
    for rc in plan.get("resource_changes", []):
        change = rc.get("change") or {}
        actions = change.get("actions", [])
        if "create" not in actions and "update" not in actions:
            continue  # no-op / read / pure delete
        after = change.get("after") or {}
        if "tags" not in after:
            continue  # resource type has no tags attribute
        tags = after["tags"] or {}
        if not tags.get(REQUIRED_TAG):
            missing.add(rc["address"])

    for address in sorted(missing):
        print(f"MISSING {REQUIRED_TAG}: {address}")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(check_plan(sys.argv[1]))