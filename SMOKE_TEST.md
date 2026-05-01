# Maneef AEC — Post-Install Smoke Test

## Environment
- Fresh ERPNext instance: YES
- Maneef installed: YES
- One Company record created: YES
- Test user roles to create: 
  - **Maneef Admin**: System Manager
  - **Project Leader**: Project Manager, Design Lead
  - **Site Lead**: Site Architect, Site Engineer

## Test Suite

### Block 1 — Role & Permission Verification
- [ ] Role **Managing Partner** exists in Role list.
- [ ] Role **Design Engineer** exists in Role list.
- [ ] Role **Doc Controller** exists in Role list.
- [ ] User with **Project Manager** role can view **Project Charter** list.
- [ ] User with **System Manager** role can view **Project Deliverable** and **Transmittal** (Verification of Fix 3).

### Block 2 — Setup Data Verification
- [ ] Navigate to **AEC Production Office** list: Confirm "Tripoli HQ" and "Cairo Production" exist.
- [ ] Navigate to **Project Type** list: Confirm 6 AEC-specific types exist.
- [ ] Navigate to **Chart of Accounts**: Confirm `1150 Work in Progress` exists for the test company.

### Block 3 — CRM & Commercial Flow
- [ ] **Create Project Charter**:
    - [ ] Create a new Project Charter.
    - [ ] Verify `naming_series` defaults to `MAN-PC-`.
    - [ ] Select a Customer and set a Budget.
    - [ ] **Save & Submit**: Verify a standard ERPNext **Project** is automatically created.
- [ ] **Create Risk Assessment**:
    - [ ] Create a Risk Assessment linked to the Charter.
    - [ ] Verify risk ratings (Payment, Commercial, Duration) can be calculated.

### Block 4 — Design & Production Flow
- [ ] **Project Deliverable**:
    - [ ] Create a new Deliverable.
    - [ ] Verify `Design Lead` can approve the record.
    - [ ] Verify status moves to "Issued" after Doc Controller check.
- [ ] **Transmittal**:
    - [ ] Create a Transmittal.
    - [ ] Link the Issued Deliverable.
    - [ ] Verify `naming_series` follows `MAN-TR-` (Verification of Fix 6).

### Block 5 — Construction & Site Management
- [ ] **Site Visit Report (SVR)**:
    - [ ] Create an SVR for an active Project.
    - [ ] Log a site issue and attach a photo.
    - [ ] Verify `System Manager` can view the report.
- [ ] **RFI Record**:
    - [ ] Create an RFI.
    - [ ] Verify it can be linked to a specific BOQ item.

### Block 6 — Financial Control
- [ ] **Project Budget Control**:
    - [ ] Verify budget utilization is visible on the Project sidebar.
    - [ ] Verify currency symbols follow the system default (Verification of Fix 4).

## Success Criteria
- All 6 blocks pass without Python Tracebacks.
- Naming series are consistent with `MAN-` prefix.
- System Manager has visibility across all custom DocTypes.
