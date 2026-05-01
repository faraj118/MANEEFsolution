# Maneef AEC — Installation Guide

## Prerequisites
- **Frappe Framework**: v15.0.0 or higher
- **ERPNext**: v15.0.0 or higher
- **ERPNext modules that must be active before install**:
  - **Projects**: Core project management (Project, Task)
  - **CRM**: Lead and Opportunity management
  - **Selling**: Customer and Sales Order processing
  - **Buying**: Purchase Order and Subcontractor management
  - **Accounting**: General Ledger and Payment Terms
  - **HR**: Employee management for Site Visit Reports

## Installation

```bash
# Step 1 — Get the app
# Replace [repo-url] with the actual repository URL
bench get-app maneef [repo-url]

# Step 2 — Install on your site
bench --site [your-site-name] install-app maneef

# Step 3 — Run migrations
bench --site [your-site-name] migrate
```

## Post-Install Configuration

1. **Verify Chart of Accounts Compliance**:
   - **What to do**: Go to **Company** list, open your company, and click the "Setup Maneef COA" button (or verify if AEC accounts like `1150 Work in Progress` exist).
   - **Where**: Accounting > Company
   - **Why**: The app requires specific AEC-compliant accounts for WIP and Salary allocation to track project financial health.

2. **Verify AEC Production Offices**:
   - **What to do**: Check if "Tripoli HQ" and "Cairo Production" offices are created. Rename or add new ones as per your organization.
   - **Where**: Design Operations > AEC Production Office
   - **Why**: These offices are linked to Site Visit Reports and Project Charters for location tracking.

3. **Check Naming Series**:
   - **What to do**: Verify that DocTypes like `Project Charter` and `Site Visit Report` use the `MAN-` prefix for new records.
   - **Where**: Core > Naming Series
   - **Why**: To prevent numbering collisions with other custom apps or standard ERPNext series.

## Default Roles Created
- Managing Partner
- Design Lead
- Technical Lead
- Doc Controller
- Site Architect
- BIM Coordinator
- Procurement Officer
- Project Coordinator
- Production Team
- Design Engineer

## Default Data Created
- **Project Types**: Innovation Projects, Landscape Projects, Small Construction, Medium Construction, Large Construction, Complex Construction.
- **Production Offices**: Tripoli HQ, Cairo Production.
- **Number Cards**: Deliverables Pending My Approval, Total Pending Approvals, High Burn Rate Projects.

## Known Limitations
- **Hardcoded Office Names**: The system initializes with "Tripoli HQ" and "Cairo Production" by default. These should be manually updated if they do not match your business structure.
- **Legacy Naming Prefixes**: Some DocTypes may still show legacy prefixes (e.g., `PC-`, `SVR-`) as options in the Naming Series select field alongside the new `MAN-` prefixes.

## Uninstallation

```bash
bench --site [your-site-name] uninstall-app maneef
bench --site [your-site-name] migrate
```

- **What the uninstaller removes**: Custom Fields on ERPNext DocTypes (Project, Customer, etc.) and Property Setters added by Maneef.
- **What must be removed manually**: All Maneef-specific DocType records (Project Charters, Transmittals, etc.) and the created AEC accounts in the Chart of Accounts to ensure the Ledger remains balanced.
