"""
Maneef AEC - Site Visit & Workspace Expansion Verification Script
================================================================
Run from bench console:
    bench --site <your-site> execute maneef.tests.verify_site_visit.run_all
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

    section("Phase 1 — Site Visit Report Schema Expansion")
    expected_fields = [
        "assigned_engineer", "visit_type", "complexity_level",
        "project", "customer", "task", "site", 
        "is_billable", "visit_cost", "attendees", "next_steps"
    ]
    
    # Try fetching doctype meta
    try:
        meta = frappe.get_meta("Site Visit Report")
        for field in expected_fields:
            has_field = meta.has_field(field)
            results.append(check(
                f"Field exists: '{field}'",
                has_field,
                "Run `bench migrate` to apply new fields."
            ))
    except Exception as e:
        results.append(check("Site Visit Report schema access", False, str(e)))

    section("Phase 2 — Backend Validation Rules")
    try:
        from maneef.construction_control.doctype.site_visit_report.site_visit_report import SiteVisitReport
        has_validate = hasattr(SiteVisitReport, "validate")
        results.append(check("Backend includes 'validate()' for billing rules", has_validate))
        
        # Simple test 
        import inspect
        source = inspect.getsource(SiteVisitReport.validate) if has_validate else ""
        results.append(check("Billing rules enforce assigned engineer and cost", "visit_cost" in source and "assigned_engineer" in source))

        source_defaults = inspect.getsource(SiteVisitReport._auto_fill_defaults)
        results.append(check("Defaults use 'assigned_engineer' parameter logic", "self.assigned_engineer" in source_defaults))
    except Exception as e:
        results.append(check("Site Visit Report python controller validation", False, str(e)))

    section("Phase 3 — AEC Architecture Square Updates")
    try:
        workspace_file = frappe.get_doc("Workspace", "aec-architecture-square")
        content_str = workspace_file.content or "[]"
        
        shortcuts_to_check = ["Projects", "Tasks", "Timesheets", "Expense Claims", "Sales Invoices", "Customers"]
        for sc in shortcuts_to_check:
            found = sc in content_str
            results.append(check(f"Workspace shortcut exists: {sc}", found, "Wait for 'bench migrate' to reload fixtures."))
    except Exception as e:
        results.append(check("Workspace parsing", False, str(e)))

    # ── Summary ──────────────────────────────────────────────────────────────
    passed = sum(results)
    total = len(results)
    section(f"SUMMARY: {passed}/{total} checks passed")
    if passed == total:
        print("\n  🎉 All checks passed! Run `bench migrate` to load the changes in Frappe.\n")
    else:
        print(f"\n  ⚠️  {total - passed} check(s) failed. Run `bench migrate` first, then re-check.\n")

    return {"passed": passed, "total": total}
