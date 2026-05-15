"""Utility for protecting deletions across DocTypes."""

import frappe


def protect_deletion(doc, dependencies):
    """Prevent deletion if linked records exist for the given document."""
    blocked = []

    for dependency in dependencies:
        doctype = dependency.get("doctype")
        link_field = dependency.get("link_field")
        label = dependency.get("label")

        if not doctype or not link_field or not label:
            continue

        count = frappe.db.count(doctype, {link_field: doc.name})
        if count > 0:
            blocked.append({"label": label, "count": count})

    if not blocked:
        return

    lines = [f"- {item['label']} ({item['count']})" for item in blocked]
    message = (
        f"Cannot delete {doc.doctype} {doc.name}. Linked records exist:\n"
        + "\n".join(lines)
        + "\nArchive this record instead of deleting."
    )

    frappe.log_error(
        message,
        title=f"Deletion blocked for {doc.doctype} {doc.name}",
    )

    raise frappe.ValidationError(message)
