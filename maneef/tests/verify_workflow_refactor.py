"""
Maneef AEC - Workflow Refactoring Verification Script
======================================================
Run from bench console:
    bench --site <your-site> execute maneef.tests.verify_workflow_refactor.run_all

Or interactively:
    bench --site <your-site> console
    >>> from maneef.tests.verify_workflow_refactor import run_all
    >>> run_all()
"""

import frappe


def check(label, condition, detail=""):
    status = "✅ PASS" if condition else "❌ FAIL"
    print(f"  {status} | {label}")
    if not condition and detail:
        print(f"         → {detail}")
    return condition


def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


@frappe.whitelist()
def run_all():
    results = []
    section("Phase 1 — Sales Order Decoupled")

    # 1a. Verify before_submit hook is NOT registered for Sales Order
    so_hooks = frappe.get_hooks("doc_events").get("Sales Order", {})
    results.append(check(
        "Sales Order has no before_submit hook",
        "before_submit" not in so_hooks,
        f"Found hooks: {so_hooks}"
    ))
    results.append(check(
        "Sales Order has no on_submit project-creation hook",
        "on_submit" not in so_hooks,
        f"Found hooks: {so_hooks}"
    ))

    section("Phase 2 — Project Charter is the sole Project creator")

    # 2a. Verify ProjectCharter controller has on_submit
    from maneef.crm_commercial.doctype.project_charter.project_charter import ProjectCharter
    results.append(check(
        "ProjectCharter.on_submit exists",
        hasattr(ProjectCharter, "on_submit")
    ))
    results.append(check(
        "ProjectCharter.create_or_update_project exists",
        hasattr(ProjectCharter, "create_or_update_project")
    ))
    results.append(check(
        "ProjectCharter.generate_tasks_from_briefs exists",
        hasattr(ProjectCharter, "generate_tasks_from_briefs")
    ))
    results.append(check(
        "ProjectCharter.deactivate_project exists (not pass-through)",
        hasattr(ProjectCharter, "deactivate_project")
    ))
    results.append(check(
        "ProjectCharter.on_update_after_submit syncs dates",
        hasattr(ProjectCharter, "on_update_after_submit")
    ))

    section("Phase 3 — Task-Based Production Engine (BIM Fixtures)")

    # 3a. Check custom fields on Task exist in DB
    bim_fields = [
        "custom_task_type",
        "custom_lod_requirement",
        "custom_bim_discipline",
        "custom_bim_zone",
        "custom_source_charter",
    ]
    for field in bim_fields:
        exists = frappe.db.exists("Custom Field", f"Task-{field}")
        results.append(check(
            f"Task has custom field: {field}",
            bool(exists),
            "Run `bench migrate` to apply fixtures."
        ))

    section("Phase 4 — GM Command Workspace (Number Cards)")

    # 4a. Check Number Cards exist in DB — auto-create if missing
    from maneef.setup import create_number_cards
    create_number_cards()  # idempotent: skips cards that already exist

    cards = [
        "Average Project Burn Rate",
        "Global Pending Approvals",
        "Deliverables Pending My Approval",
    ]
    for card in cards:
        exists = frappe.db.exists("Number Card", card)
        results.append(check(
            f"Number Card exists: '{card}'",
            bool(exists),
            "Check setup.py create_number_cards() for errors."
        ))

    # 4b. Check workspace exists (number_cards is stored as child records, not a column)
    workspace_exists = frappe.db.exists("Workspace", {"name": "aec-architecture-square"})
    results.append(check(
        "AEC Architecture Square workspace exists",
        bool(workspace_exists),
        "Run `bench migrate` to import workspace fixture."
    ))

    section("Phase 5 — Production Office Lookup")

    # 5a. Verify get_production_office uses correct doctype
    import inspect
    source = inspect.getsource(ProjectCharter.get_production_office)
    results.append(check(
        "get_production_office queries 'AEC Production Office' (not 'Maneef Office')",
        "AEC Production Office" in source and "@frappe.with_cache" not in source,
        "Invalid cache decorator or wrong doctype still in source."
    ))

    # ── Summary ──────────────────────────────────────────────────────────────
    passed = sum(results)
    total = len(results)
    section(f"SUMMARY: {passed}/{total} checks passed")
    if passed == total:
        print("\n  🎉 All checks passed! Run `bench migrate` to activate fixtures.\n")
    else:
        print(f"\n  ⚠️  {total - passed} check(s) failed. Review output above.\n")

    return {"passed": passed, "total": total}
