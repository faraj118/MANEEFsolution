"""Product utility for permission checks on ignored-permissions methods."""

import functools

import frappe


def require_permission(doctype, ptype="write", required_roles=None):
    """Decorator to enforce permission checks before allowing a call."""

    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            user = frappe.session.user
            allowed = frappe.has_permission(doctype, ptype=ptype)

            if required_roles:
                roles = set(frappe.get_roles())
                required = set(required_roles)
                allowed = allowed and bool(roles & required)

            frappe.logger().info(
                "Permission check: user=%s doctype=%s ptype=%s allowed=%s",
                user,
                doctype,
                ptype,
                allowed,
            )

            if not allowed:
                raise frappe.PermissionError(
                    f"User {user} does not have {ptype} permission for {doctype}."
                )

            return fn(*args, **kwargs)

        return wrapper

    return decorator
