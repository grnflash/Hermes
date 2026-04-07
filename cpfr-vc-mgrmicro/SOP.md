# CPFR VC Vendor Info Manager -- Standard Operating Procedure

**Audience:** Instock Managers (ISMs), Category Managers (CMs), and VC personnel who maintain vendor distribution and contact data for CPFR communications.

**Confidentiality:** Chewy Confidential -- For Internal Use Only

---

## 1. Purpose

The **CPFR VC Vendor Info Manager** is the intended interface for maintaining the VC-CPFR vendor information that drives email distribution for automated reports and VC communications. It is designed to make this work fast, accurate, and safe -- with built-in validation, a confirmation step before anything is saved, and a complete audit trail for every change.

Using this tool rather than direct database access is the right approach. It surfaces the right fields, enforces the right formats, prevents a category of common mistakes, and keeps a record that makes corrections straightforward. The CPFR team expects this to be the standard method going forward.

---

## 2. Access

Open the **CPFR VC Vendor Info Manager** through Snowflake -- navigate to **Projects > Streamlit Apps** and select the app from the list.

If the app fails to load or returns a connection error, confirm that your Snowflake session is active and that your network allows Snowflake traffic. If access problems persist, contact the CPFR team or your Snowflake administrator.

---

## 3. How the Tool Works

### 3.1 Vendor tiers (FILE)

Each vendor record has a **FILE** value that determines its CPFR distribution tier and cadence. The options are:

| FILE | What it means |
|------|---------------|
| **Tier1** | Managed at the parent-company level. Tier1 records require CPFR vetting before they are created or reclassified, because the way vendor identity is keyed for Tier1 differs from other tiers. **You cannot set a record to Tier1 in this app** -- contact CPFR. |
| **Tier2** | Standard individual-vendor tier. |
| **6Months** | Six-month cadence tier. |
| **None** | No tier assigned. |

### 3.2 Email fields and how they control distribution

- **Vendor Contacts** is the primary recipient list for CPFR emails on that record.
- If **Override Email** is filled in, it takes over completely -- only those addresses receive reports, and Vendor Contacts is bypassed until Override Email is cleared.
- The other email fields (Category Manager, In-Stock Manager, and their respective AD emails) are maintained for visibility and downstream use.
- All email fields accept multiple addresses in **semicolon-separated** format: `first@chewy.com;second@chewy.com`

### 3.3 Making and confirming changes

Edits follow a deliberate two-step flow to prevent accidental saves:

1. Open a vendor record from search or the table view and make your changes.
2. Click **Save Changes** -- nothing is written yet. The app shows a **Changes Summary** listing every field with its old and new value.
3. Review the summary, then click **Confirm Changes** to save, or **Cancel Changes** to discard.
4. A **receipt** screen appears after a successful save. It shows exactly what changed and the record's current state. This is your best opportunity to catch something wrong before you move on -- if you spot an error, you can go right back and make another edit.

Adding a new vendor works similarly but completes on a single screen with an inline confirmation rather than a separate receipt.

---

## 4. Search: Find a specific vendor

From the **Search** screen, choose how you want to look up the vendor:

- **Vendor Number** -- exact, case-sensitive match. Type the full vendor number as it is stored.
- **Vendor Name**, **Parent Company**, **Vendor Contacts** -- partial, case-insensitive match. Any fragment works.

Enter your term and click **Search**. Results show the vendor number, name, and FILE for each matching record. Click **Edit** on the record you want to open.

**When you see duplicate labels:** If a vendor number has more than one record, the lower-priority rows are tagged `(duplicate)` or similar. Pick the record with the FILE you intend to edit, and flag the duplication to CPFR if cleanup is needed.

**Back to Search** returns you to the search screen and clears the result list.

---

## 5. Table view: Browse and filter all vendors

Click **View full table** from Search to load every vendor record into a sortable, filterable grid.

**Filtering:** Expand **Filters** to narrow the list. Type a partial value in any column's text box, or select from the **FILE** multiselect. Filters stack -- every field you fill in narrows the results further, so you can, for example, show only Tier2 records whose vendor name contains "Pet" at the same time.

**Opening a record:** Click any row in the grid to open it directly in the editor.

**Sorting:** Click any column header to sort by that column.

**After saving changes:** The table does not auto-refresh. Click **Refresh data** to pull the latest values from the database.

Filter settings are preserved when you leave to edit a record and come back, so you can continue working the same narrowed view.

**Back to Search** clears filters and returns to the search screen.

---

## 6. Edit a vendor record

Open the editor from a search result or from the table view. The record is reloaded fresh from the database when you open it.

### 6.1 Editable fields

The following fields can be edited. **Vendor Number** is not editable -- it identifies the record.

- **Vendor Name**
- **Vendor Contacts** *(required; semicolon-separated emails)*
- **Parent Company**
- **Category Manager Email**
- **Category Merch AD Email**
- **In-Stock Manager Email**
- **In-Stock AD Email**
- **Override Email**

**FILE** (the tier) is also editable, with one restriction -- see below.

### 6.2 Email fields

Enter multiple addresses separated by semicolons: `alice@chewy.com;bob@chewy.com`. The app validates format, normalizes addresses (for example lowercasing the domain), removes duplicates, and sorts the list before saving. Leave a field empty to clear it (blank / null).

### 6.3 Changing the tier (FILE)

You can change a record's FILE value -- it updates in place. **Switching to Tier1 is not permitted in this app.** Tier1 requires CPFR involvement because Tier1 records are keyed by parent company rather than individual vendor number, and the data needs to be verified before that classification is applied. Contact CPFR using the link shown when you select Tier1 in the dropdown.

### 6.4 Save, confirm, and receipt

1. Click **Save Changes**. The app validates your input and shows a **Changes Summary** -- review it.
2. Click **Confirm Changes** to write the update, or **Cancel Changes** to discard.
3. After a successful save, the **receipt** screen shows what changed (old value to new value for each field) and the full current state of the record. If you notice an error, navigate back and make a correcting edit right away -- you do not need to contact CPFR unless you are unsure what the correct value should be.

---

## 7. Add a new vendor

To add a vendor, you must first confirm it does not already exist:

1. On **Search**, select **Vendor Number** and enter the exact vendor number.
2. Click **Search**. If no match is found, **Create New Entry** appears.
3. Click **Create New Entry**. The vendor number is pre-filled and locked.
4. Select a **FILE** value. Tier1 is not available on new records -- select Tier2, 6Months, or None.
5. Fill in the required fields: **Vendor Name** and **Vendor Contacts**.
6. Add any optional fields (Parent Company, email fields) as needed.
7. Click **Create Vendor**. A confirmation and summary appear on the same screen.

The exact-match search requirement in step 1 is intentional: it ensures the vendor number does not already exist under that precise identifier before any new data is created. This prevents records like P12345 and B12345 from being confused, and catches partial or abbreviated numbers before they become permanent.

---

## 8. Built-in guardrails

The app includes several features that protect data quality:

- **New-vendor gate:** Create New Entry is only offered after a Vendor Number search returns no results, confirming the exact identifier is not already in use.
- **Email validation:** All email fields are validated for format and normalized before saving. Errors are shown inline.
- **Required fields:** Vendor Name and Vendor Contacts must be provided on new records.
- **Tier1 restriction:** Tier1 cannot be set from this app. CPFR must vet and create Tier1 records directly.
- **Two-step save:** Changes are previewed in a summary before anything is committed. There is no single-click path to overwriting a record.
- **Duplicate detection:** When a vendor number appears on more than one record, the lower-priority rows are labeled in search results.

---

## 9. Change history

Every action in the tool -- whether it succeeds or fails -- is logged automatically. The log captures who made the change, which fields were affected, and the before and after values of the record.

**If you make a mistake:** If you know what went wrong and what the correct value is, simply edit the record again. The tool supports as many corrections as you need. Contact CPFR when you are unsure what was changed, cannot determine the correct state, or want someone to verify the history before you act. CPFR can review the log and, if needed, restore a prior state -- but that escalation is for the unclear cases, not every error.

---

## 10. Troubleshooting

| Symptom | What to try |
|---------|-------------|
| App will not load | Verify your Snowflake session is active and your network allows Snowflake traffic. Retry after a moment. |
| Search returns no results | For Vendor Number, confirm the exact string and capitalization. For other search types, try a shorter fragment. |
| Create New Entry does not appear | Use **Vendor Number** search and run the search first. The button appears only after a zero-result search. |
| Cannot select Tier1 | By design. Contact CPFR using the in-app link. |
| Changes are not saving | Check inline error messages. Confirm you clicked both **Save Changes** and then **Confirm Changes**. |
| Table shows stale values | Click **Refresh data** on the table view. |

---

## 11. Support

For Tier1 requests, questions about correct data, or help understanding a prior change, contact the **CPFR team** using the contact information shown in the app.

When you reach out, include: the vendor number, approximately when the change occurred, what you expected vs. what you see, and a screenshot of the receipt or Changes Summary if you have one.

---

*Last updated: April 2026*
