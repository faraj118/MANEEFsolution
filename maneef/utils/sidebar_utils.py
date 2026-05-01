import frappe


def get_gate_badge_color(gate_status):
    colors = {
        "Gate 1": "#3b82f6",
        "Gate 2": "#8b5cf6",
        "Gate 3": "#06b6d4",
        "Complete": "#10b981",
    }
    return colors.get(gate_status, "#64748b")


def get_risk_badge_color(rating):
    colors = {
        "Low": "#10b981",
        "Green": "#10b981",
        "Medium": "#f59e0b",
        "Amber": "#f59e0b",
        "High": "#ef4444",
        "Red": "#ef4444",
        "Unacceptable": "#ef4444",
        "Critical": "#ef4444",
    }
    return colors.get(str(rating), "#64748b")


def build_sidebar_html(items):
    html = '<div style="padding:12px 0;">'
    for item in items:
        label = item.get("label", "")
        value = item.get("value", "")
        color = item.get("color", "#64748b")
        html += f'''
        <div style="margin-bottom:10px;">
            <div style="font-size:11px;color:#94a3b8;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:2px;">{label}</div>
            <div style="font-size:13px;font-weight:600;color:{color};">{value}</div>
        </div>'''
    html += '</div>'
    return html


def build_link_html(links):
    html = '<div style="padding:8px 0;border-top:1px solid #1e293b;margin-top:8px;">'
    html += '<div style="font-size:10px;color:#64748b;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px;">Related Records</div>'
    for link in links:
        label = link.get("label", "")
        doctype = link.get("doctype", "")
        field = link.get("field", "")
        html += f'''
        <div style="margin-bottom:6px;">
            <a href="/app/{doctype.lower().replace(" ", "-")}"
               style="font-size:12px;color:#60a5fa;text-decoration:none;"
               onclick="frappe.set_route('List', '{doctype}', {{'{field}': cur_frm.doc.name}});return false;">
                {label} &rarr;
            </a>
        </div>'''
    html += '</div>'
    return html
