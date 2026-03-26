import os
import json
import glob

base_dir = r"\\wsl.localhost\Ubuntu\home\falbu\frappe_docker\development\frappe-bench\apps\maneef\maneef"

# Standard permissions to inject
standard_permissions = [
    {
        "create": 1, "delete": 1, "email": 1, "export": 1, "print": 1, "read": 1, "report": 1,
        "role": "System Manager", "share": 1, "write": 1
    },
    {
        "create": 1, "delete": 0, "email": 1, "export": 1, "print": 1, "read": 1, "report": 1,
        "role": "Managing Partner", "share": 1, "write": 1
    },
    {
        "create": 1, "delete": 0, "email": 1, "export": 1, "print": 1, "read": 1, "report": 1,
        "role": "Project Manager", "share": 1, "write": 1
    }
]

# Naming auto-names map
autoname_map = {
    "Project Charter": "format:PC-{YYYY}-{####}",
    "Rfi Record": "format:RFI-{YYYY}-{####}",
    "Site Visit Report": "format:SVR-{YYYY}-{MM}-{####}",
    "Transmittal": "format:TR-{YYYY}-{####}",
    "Stop Work Notice": "format:SWN-{YYYY}-{####}"
}

for json_path in glob.glob(os.path.join(base_dir, "**", "doctype", "**", "*.json"), recursive=True):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    doc_name = data.get("name")
    if not doc_name:
        continue
    
    modified = False

    # 1. Update Permissions if istable is false or missing
    if not data.get("istable"):
        if "permissions" not in data or len(data["permissions"]) == 0:
            data["permissions"] = standard_permissions
            modified = True
            print(f"Added permissions to {doc_name}")

    # 2. Add Autoname (format string)
    if doc_name in autoname_map:
        if "autoname" not in data or data["autoname"] != autoname_map[doc_name]:
            data["autoname"] = autoname_map[doc_name]
            modified = True
            print(f"Added autoname {autoname_map[doc_name]} to {doc_name}")

    if modified:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=1)
            
print("Done updating doctypes.")
