# CPFR VC Vendor Info Manager — AI Context

**Project**: cpfr-vc-mgrmicro
**Purpose**: Streamlit-in-Snowflake app for managing CPFR vendor contact assignments (email addresses, tier, chargeback dates).
**Phase**: Production
**Key Files**: `streamlit_app.py`, `database_manager.py`, `vendor_processor.py`, `environment.yml`
**Active Work**: Cosmetic/UX improvements (button color scheme, field aliasing, SOP link)

---

## Quick Reference

### Data Model
- One row per `(Vendor Number, FILE)` in the source table.
- `FILE` is the database column name for what the UI calls **Tier** (`Tier1`, `Tier2`, `6Months`, `None`). Always use `FILE` in SQL/Python; always display as `Tier` in the UI. The mapping lives in `FIELD_DISPLAY_NAMES` in `streamlit_app.py`.
- `3Months` is a legacy value normalized to `6Months` on read.

### State Machine
The app is a simple state machine driven by `st.session_state.current_mode`:
```
search -> results -> edit -> receipt
search -> new
search -> tabular -> edit -> receipt
```
Back-navigation is always explicit (no browser back button). Edit origin is tracked in `st.session_state.edit_origin` (`"search_results"` | `"tabular"` | `None`) to route the back button correctly.

### Connection
SiS only — uses `get_active_session()`. Never use `snowflake.connector.connect()` here.

---

## Button Color Scheme

### The Four Tiers

| Color | When to use | How to assign |
|---|---|---|
| **Blue** (primary) | Default next step in the workflow | `type="primary"` |
| **Tan** (bronze) | Non-default forward/utility actions | `type="secondary"`, key prefixed `btn_tan_` |
| **Gunmetal** (dark slate) | All "Back to ..." backward navigation | `type="secondary"`, key prefixed `btn_back_` |
| **Purple** | "View full table" exclusively | `type="secondary"`, key `btn_view_full_table` |

### Why Key-Prefix CSS — The Hard-Won Lesson

**What was tried first and why it failed:**

`button[data-testid="baseButton-secondary"]` — Streamlit does emit this `data-testid` on the `<button>` element, but the selector has CSS specificity `(0,1,1)`. Streamlit's own emotion-cache stylesheet injects rules at the same or higher specificity, and because it loads *after* our injected `<style>` block, it wins on source order. Adding `!important` helps in some cases but not all — SiS pins an older Streamlit build that injects some of its own `!important` rules for the default secondary button appearance, creating an unresolvable collision.

`button[kind="secondary"]` — `kind` is a React prop consumed at the component level. It is **never emitted as a DOM attribute** on the rendered `<button>` element. This selector matches nothing.

**What works and why:**

Streamlit wraps every keyed widget in a `div` with class `st-key-{key}`. A selector like `[class*="st-key-btn_tan_"] button` is a **descendant selector** with specificity `(0,1,1)` — one attribute class match on the parent div, one element match on the button. Because it is a descendant selector (not a flat button rule), it wins over any rule targeting the button in isolation, regardless of source order or the Streamlit version. This is consistent across all container types: columns, expanders, forms, and plain page layout.

**The CSS lives in `main()` immediately after `st.set_page_config()`**, injected via `st.markdown(..., unsafe_allow_html=True)`. It uses three wildcard prefix rules plus one exact-match rule for purple:

```css
[class*="st-key-btn_tan_"] button  { /* tan */ }
[class*="st-key-btn_back_"] button { /* gunmetal */ }
.st-key-btn_view_full_table button { /* purple */ }
```

**Adding a new button:** Give it a key with the right prefix. No CSS changes needed.

```python
# Tan example
st.button("Export CSV", type="secondary", key="btn_tan_export_csv")

# Gunmetal example
st.button("← Back to Search", type="secondary", key="btn_back_search_foo")

# form_submit_button also supports key=
st.form_submit_button("← Back", key="btn_back_my_form")
```

### Current Button Inventory

| Button | Screen | Color | Key |
|---|---|---|---|
| Search | Search | Blue | — |
| View full table | Search | Purple | `btn_view_full_table` |
| Create New Entry | Search | Blue | — |
| Edit (×N) | Results | Blue | `edit_{i}` |
| Back to Search | Results | Gunmetal | `btn_back_search_from_results` |
| Back to Search | Tabular | Gunmetal | `btn_back_search_tabular` |
| Refresh data | Tabular | Blue | `tabular_refresh` |
| Clear all filters | Tabular | Tan | `btn_tan_clear_filters` |
| Open selected row in editor | Tabular | Blue | `browse_open_{nonce}` |
| Save Changes (form) | Edit | Blue | — |
| Back to … (form) | Edit | Gunmetal | `btn_back_edit_form` |
| Confirm Changes | Edit | Blue | — |
| Cancel Changes | Edit | Tan | `btn_tan_cancel_changes` |
| Continue in table view | Receipt | Tan | `btn_tan_continue_table` |
| Back to Search | Receipt | Blue or Gunmetal* | `btn_back_search_receipt` |
| Back to search results | Receipt | Blue | `btn_back_results_receipt` |
| Create Vendor (form) | New entry | Blue | — |
| Back to Search (form) | New entry | Gunmetal | `btn_back_new_entry_form` |

*Receipt "Back to Search" is blue (`type="primary"`) only when there are no search results and no tabular origin — i.e., it is the sole available exit. Otherwise it is gunmetal.

---

## Field Display Name Mapping

Database column names are aliased for display in `FIELD_DISPLAY_NAMES` at the top of `streamlit_app.py`. Always use `get_field_display_name(field)` when rendering a field label in the UI. Never hardcode display names inline.

```python
FIELD_DISPLAY_NAMES = {
    'FILE': 'Tier',
    'Parent Vendor': 'Parent Company',
    'CM_Email': 'Category Manager Email',
    'CM Manager_Email': 'Category Merch AD Email',
    'SP_Email': 'In-Stock Manager Email',
    'SP Manager_Email': 'In-Stock AD Email',
    'OVERRIDE_EMAIL': 'Override Email',
}
```

---

## Override Email Field

The `OVERRIDE_EMAIL` field has a placeholder string (`OVERRIDE_EMAIL_PLACEHOLDER`) that explains its semantics to users. Key points to preserve in any rewording:
- Addresses here **replace** Vendor Contacts, not supplement them.
- The field is **not updated** by batch uploads — it is durable.
- It has **no effect** on VC/Chargeback apps.
- Leave empty to restore normal Vendor Contacts routing.

---

## Tier Info Expander (Edit Screen)

On the edit screen, `col2` next to the Tier selectbox shows either:
- A Tier1 authorization error (if user is trying to change to Tier1)
- An `ℹ️ About Tiers` expander with `TIER_INFO_MARKDOWN` (a compact metrics table)
- Nothing (if already Tier1 and not changing)

The expander is intentionally absent when a Tier1 error is shown, to avoid visual clutter.

---

## SOP & Support

The `📖 SOP & Support` expander at the bottom of the search screen contains:
- SOP SharePoint link (live URL, not a placeholder)
- CPFR Program Lead: nmiles1@chewy.com
- VC/Chargeback Program Lead: nnelson2@chewy.com

Update these when the SOP URL changes or contacts change.

---

## Known Constraints

- **Tier1 changes are blocked** in the UI unless the vendor is already Tier1. The block is enforced in both `save_vendor_changes()` and `save_new_vendor()`.
- **Duplicate rows** (same Vendor Number, different FILE) are shown with a `duplicate_label` in search results. Cleanup is a database-side concern; the app only flags them.
- **`3Months` FILE value** is a legacy value. It is normalized to `6Months` on read in `show_edit_screen()` and `save_vendor_changes()`. Do not add `3Months` to the selectbox options.
