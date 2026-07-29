# FTTH Support & Commercial Helpdesk Enhancement

**Module Name:** `skyline_helpdesk_enhancment`  
**Target Version:** Odoo 19.0  
**Directory Path:** `\\wsl.localhost\Ubuntu\home\zack\addon\skyline_helpdesk_enhancment`  
**Date:** July 27, 2026  

---

## 1. Executive Summary & Objective

This module customizes Odoo 19 Helpdesk to serve Fiber to the Home (FTTH) support and commercial teams. It allows toggling FTTH configuration on specific Helpdesk teams, restricts customer selection on FTTH tickets to designated FTTH customers, and automatically syncs technical subscription data (Username, Serial Number, Activation Code, Package, Zone, FAT) from the contact record onto the ticket.

---

## 2. Models & Data Structure

### A. `ftth.package` (New Model)
* **Description:** Configuration model for FTTH subscription packages linked to service products.
* **Fields:**
  * `name` (`Char`, required): Package name (e.g., "Fiber 100Mbps Ultra").
  * `product_id` (`Many2one` -> `product.product`): Service product (domain: `[('type', '=', 'service')]`).
  * `active` (`Boolean`, default=True): Active status.
  * `notes` (`Text`): Package notes or SLA details.

### B. `res.partner` (Extension)
* **Fields Added:**
  * `is_ftth_customer` (`Boolean`, default=False): Flag identifying FTTH customers.
  * `ftth_package_id` (`Many2one` -> `ftth.package`): Customer's FTTH package.
  * `ftth_username` (`Char`): Customer PPPoE/Service username.
  * `ftth_serial_number` (`Char`): ONT/Router serial number.
  * `ftth_activation_code` (`Char`): Service activation code.
  * `ftth_zone_id` (`Many2one` -> `account.analytic.account`): Analytic zone account.
  * `ftth_fat` (`Char`): Fiber Access Terminal identifier.

### C. `helpdesk.team` (Extension)
* **Fields Added:**
  * `is_ftth_team` (`Boolean`, default=False): Toggle on team configuration view to enable FTTH specific logic.

### D. `helpdesk.ticket` (Extension)
* **Fields Added:**
  * `is_ftth_team` (`Boolean`, related `team_id.is_ftth_team`, stored): Identifies if current ticket belongs to an FTTH team.
  * `ftth_package_id` (`Many2one` -> `ftth.package`)
  * `ftth_username` (`Char`)
  * `ftth_serial_number` (`Char`)
  * `ftth_activation_code` (`Char`)
  * `ftth_zone_id` (`Many2one` -> `account.analytic.account`)
  * `ftth_fat` (`Char`)
* **Automations & Logic:**
  * **Onchange Sync:** Selecting or changing `partner_id` on an FTTH ticket automatically populates all FTTH fields from the customer record.
  * **Create Sync:** Overridden `create()` method ensures tickets created via API, web, or backend with an FTTH team automatically inherit FTTH values from the contact.

---

## 3. UI & Views

### A. Contact View (`views/res_partner_views.xml`)
* Added `is_ftth_customer` boolean switch to contact header.
* Added dedicated **FTTH Details** page in notebook (visible when `is_ftth_customer = True`).
* Added **FTTH Customers** search filter in contacts list view.

### B. Helpdesk Team View (`views/helpdesk_team_views.xml`)
* Added **FTTH Configuration Enabled** toggle (`is_ftth_team`).
* Added dynamic banner alert notifying users when FTTH configuration is active for the team.

### C. Helpdesk Ticket View (`views/helpdesk_ticket_views.xml`)
* Dynamic Customer Domain:
  ```xml
  <attribute name="domain">['|', ('team_id.is_ftth_team', '=', False), ('is_ftth_customer', '=', True)]</attribute>
  ```
  *(If the ticket team is NOT an FTTH team, all contacts are shown; if it IS an FTTH team, ONLY contacts with `is_ftth_customer = True` appear).*
* Added dedicated **FTTH Details** page in ticket notebook (visible when `is_ftth_team = True`).

### D. FTTH Packages View & Menu (`views/ftth_package_views.xml`)
* Tree/List & Form views for `ftth.package`.
* Added menu item under **Helpdesk → Configuration → FTTH Packages**.

### E. Settings View (`views/res_config_settings_views.xml`)
* Added FTTH section in Helpdesk Settings with a shortcut to manage FTTH Packages.

---

## 4. File Directory Structure

```
skyline_helpdesk_enhancment/
├── __init__.py
├── __manifest__.py
├── README.md
├── models/
│   ├── __init__.py
│   ├── ftth_package.py
│   ├── helpdesk_team.py
│   ├── helpdesk_ticket.py
│   ├── res_config_settings.py
│   └── res_partner.py
├── security/
│   └── ir.model.access.csv
└── views/
    ├── ftth_package_views.xml
    ├── helpdesk_team_views.xml
    ├── helpdesk_ticket_views.xml
    ├── res_config_settings_views.xml
    └── res_partner_views.xml
```

---

## 5. Instructions for Next AI Agent / Developer

1. **Module Upgrade:** Update the module in your Odoo 19 instance:
   ```bash
   odoo-bin -c /path/to/odoo.conf -u skyline_helpdesk_enhancment -d <database_name>
   ```
2. **Testing Workflow:**
   * Go to **Helpdesk → Configuration → Helpdesk Teams**, open a team, and check **FTTH Configuration Enabled**.
   * Go to **Contacts**, create or edit a contact, check **Is FTTH Customer**, and fill in FTTH technical details & package.
   * Create a new Helpdesk Ticket under the FTTH team. Verify that the Customer dropdown only shows FTTH customers, and that selecting a customer automatically copies all FTTH details into the ticket's **FTTH Details** tab.
