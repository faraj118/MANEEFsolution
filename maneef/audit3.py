import os
import re
import json

app_path = "/workspace/development/frappe-bench/apps/maneef/maneef"
js_files = []
for root, dirs, files in os.walk(app_path):
    for f in files:
        if f.endswith(".js") and not "/node_modules/" in root:
            js_files.append(os.path.join(root, f))

# regex for frappe.ui.form.on("DocType"
form_on_re = re.compile(r'frappe\.ui\.form\.on\([\'"]([^\'"]+)[\'"]')

# regexes for field accesses
field_res = [
    re.compile(r'frm\.doc\.([a-zA-Z0-9_]+)'),
    re.compile(r'frm\.set_value\([\'"]([a-zA-Z0-9_]+)[\'"]'),
    re.compile(r'frm\.get_field\([\'"]([a-zA-Z0-9_]+)[\'"]'),
    re.compile(r'frm\.fields_dict\[[\'"]([a-zA-Z0-9_]+)[\'"]\]'),
    re.compile(r'frm\.set_df_property\([\'"]([a-zA-Z0-9_]+)[\'"]'),
    re.compile(r'frappe\.model\.set_value\([^,]+,\s*[^,]+,\s*[\'"]([a-zA-Z0-9_]+)[\'"]'),
    re.compile(r'cur_frm\.fields_dict\[[\'"]([a-zA-Z0-9_]+)[\'"]\]'),
]

# Map DocType name to its JSON path
doctype_json_map = {}
for root, dirs, files in os.walk(app_path):
    for f in files:
        if f.endswith(".json"):
            dt_name = f.replace(".json", "").replace("_", " ").title()
            doctype_json_map[dt_name] = os.path.join(root, f)

# Also load standard doctypes we might reference (Project, Sales Order, Customer)
# If we don't have them in maneef, we just assume they exist or check custom fields
standard_doctypes = ["Project", "Sales Order", "Customer", "Task", "Company", "Issue"]
for root, dirs, files in os.walk("/workspace/development/frappe-bench/apps/erpnext/erpnext"):
    for f in files:
        if f.endswith(".json") and "/doctype/" in root:
            dt_name = f.replace(".json", "").replace("_", " ").title()
            if dt_name in standard_doctypes:
                doctype_json_map[dt_name] = os.path.join(root, f)

for root, dirs, files in os.walk("/workspace/development/frappe-bench/apps/frappe/frappe"):
    for f in files:
        if f.endswith(".json") and "/doctype/" in root:
            dt_name = f.replace(".json", "").replace("_", " ").title()
            if dt_name in standard_doctypes:
                doctype_json_map[dt_name] = os.path.join(root, f)

# Additionally, load custom fields from maneef/maneef/custom/custom_fields.json if it exists (or hooks)
custom_fields = {}
# actually maneef might add custom fields to standard doctypes via fixtures/custom_field.json
for root, dirs, files in os.walk(app_path):
    for f in files:
        if f == "custom_field.json":
            with open(os.path.join(root, f)) as jf:
                try:
                    cfs = json.load(jf)
                    for cf in cfs:
                        dt = cf.get("dt")
                        fn = cf.get("fieldname")
                        if dt not in custom_fields: custom_fields[dt] = []
                        custom_fields[dt].append(fn)
                except: pass

print("--- AUDIT START ---")
for js_file in js_files:
    with open(js_file, "r") as f:
        content = f.read()

    # Find doctypes targeted by this JS file
    doctypes = form_on_re.findall(content)
    if not doctypes:
        # Maybe it's named like the doctype
        base = os.path.basename(js_file).replace("_sidebar.js", "").replace(".js", "").replace("_", " ").title()
        doctypes = [base]

    fields_found = set()
    for regex in field_res:
        fields_found.update(regex.findall(content))

    # ignore common standard fields or js functions
    ignore_list = ["name", "owner", "creation", "modified", "modified_by", "docstatus", "idx", "parent", "parenttype", "parentfield"]
    fields_found = [f for f in fields_found if f not in ignore_list]

    for dt in doctypes:
        if dt in doctype_json_map:
            with open(doctype_json_map[dt], "r") as jf:
                try:
                    schema = json.load(jf)
                    valid_fields = [field.get("fieldname") for field in schema.get("fields", [])]
                except Exception as e:
                    print(f"Error loading {doctype_json_map[dt]}: {e}")
                    continue
        else:
            # We don't have the schema (e.g. standard ERPNext doctype and we didn't find it)
            valid_fields = []

        # Add custom fields if any
        if dt in custom_fields:
            valid_fields.extend(custom_fields[dt])

        if not valid_fields: continue

        for field in fields_found:
            if field not in valid_fields:
                # Also ignore js functions commonly attached to doc
                if field in ["__islocal", "__onload", "get_formatted", "amended_from"]: continue
                print(f"📍 Location: {js_file} ↔ {doctype_json_map.get(dt, 'Unknown JSON')}")
                print(f"❌ Issue type: Field drift")
                print(f"🔎 Detail: JS references '{field}', which does not exist in {dt} schema.")
                print(f"✅ Fix: Check if typo or missing field in '{dt}'.\n")

print("--- AUDIT END ---")
