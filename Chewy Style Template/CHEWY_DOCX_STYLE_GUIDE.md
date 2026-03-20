# Chewy CPFR Project — Document Style Guide
**Version 1.0 — Locked 2026-03-17**

---

## 1. Files in This Style System

| File | Purpose |
|---|---|
| `chewy_docx_style.js` | Canonical style module — import into any build script |
| `build_template.js` | Builds `chewy_style_template.docx` — the style carrier |
| `chewy_style_template.docx` | Style specimen document — use for Word template export |
| `chewy_style_template.dotx` | *(manually created — see Section 3)* Word template for style import |

---

## 2. Using the Style Module in a New Build Script

```javascript
const { Document, Packer } = require('docx');
const fs = require('fs');
const S = require('./chewy_docx_style');

const doc = new Document({
  numbering:  S.docNumbering(),
  styles:     S.docStyles(),
  sections: [{
    properties: S.docPageProps(),
    headers:    { default: S.docHeader("My Document Title", "Draft v1.0 — Internal Review") },
    footers:    { default: S.docFooter() },
    children: [
      S.h1("Document Title"),
      // Byline metadata table
      new Table({
        width: { size: S.CONTENT_WIDTH, type: WidthType.DXA },
        columnWidths: [1800, S.CONTENT_WIDTH - 1800],
        rows: [
          S.metaRow("Authors:", "Nathan Miles (CPFR), Nathan Nelson (VC)"),
          S.metaRow("Sponsor:", "Dave Livesay, Sr. Director, Inventory Management"),
          S.metaRow("Date:",    "March 2026"),
          S.metaRow("Status:", "Draft v1.0 — For Internal Review"),
        ]
      }),
      S.h2("1. Section Heading"),
      S.bodyPara("Body text paragraph."),
      S.h3("1.1 Sub-section Heading"),
      S.bullet1("Bullet item"),
      S.bullet2("Sub-bullet item"),
    ]
  }]
});

Packer.toBuffer(doc).then(buf => fs.writeFileSync('output.docx', buf));
```

### Column width reminder
All `columnWidths` arrays must sum to `S.CONTENT_WIDTH` (10,512 DXA).  
Preset column arrays are in `S.COLS`:

| Key | Widths | Use for |
|---|---|---|
| `S.COLS.T4_DEPENDENCY` | [3200, 2600, 2000, 2712] | Dependency chain table |
| `S.COLS.T3_STANDARD` | [3800, 3356, 3356] | Entitlement / 3-col general |
| `S.COLS.T3_LOE` | [3800, 3012, 3700] | LOE / action tables |
| `S.COLS.T2_COMPARE` | [2200, 4156, 4156] | Funding comparison |

---

## 3. Creating the Word Template (.dotx) — Manual Step

The `.dotx` file cannot be produced programmatically — Word must save it.

1. Open `chewy_style_template.docx` in Word
2. **File → Save As**
3. Change file format to **Word Template (.dotx)**
4. Save as `chewy_style_template.dotx` in a location you'll remember  
   *(suggested: `~/Library/Group Containers/UBF8T346G9.Office/User Content/Templates/`  
   — this is Word's default personal templates folder on Mac)*

That's it. The `.dotx` is now available as "My Templates" when creating new documents.

---

## 4. Applying This Style Set to an Existing Document — Manual Steps

Word's style import mechanism copies style definitions from one document into another, overriding any conflicting styles by name. This works cleanly on any document where headings were tagged with Word's built-in style names (Heading 1, Heading 2, Normal, etc.).

### Steps:

1. Open the **target document** (the one you want to restyle) in Word
2. Go to **Format → Style** (Mac) or **Home → Styles pane → Manage Styles** (Windows)
3. Click **Import/Export...**  
   *(On Mac: in the Style dialog, click the Organizer button)*
4. The **Organizer** dialog opens. You'll see two panes — left = current document, right = Normal.dotm (default template)
5. On the **right pane**, click **Close File**, then **Open File**
6. Navigate to `chewy_style_template.dotx` and open it
7. In the right pane you'll now see the Chewy styles listed
8. Select the styles you want to copy (Cmd+click to multi-select):
   - `Heading 1`
   - `Heading 2`
   - `Heading 3`
   - `Heading 4`
   - `Normal`
   - `Body Text 2`
9. Click **Copy →** to copy them into the target document
10. When prompted "overwrite existing style?", click **Yes to All**
11. Close the Organizer and save the document

### What this will and won't fix:
- ✅ Any paragraph already tagged with a style name (Heading 1, Normal, etc.) will immediately reformat to match the Chewy style
- ✅ Tables will retain their structure; cell paragraphs tagged Normal will reformat
- ❌ Manually-formatted text (bold applied directly, not via style) will NOT reformat — it has no style tag to match against
- ❌ Page margins and line numbering are section properties, not styles — see Section 5 below

---

## 5. Per-Document Manual Tweaks in Word

Even after style import, two settings must be set manually per document because they are section properties, not paragraph styles:

### Page margins and gutter
1. **Format → Document** (Mac) or **Layout → Margins → Custom Margins** (Windows)
2. Set: Top `0.5"` / Bottom `0.5"` / Left `0.5"` / Right `0.5"` / Gutter `0.2"`
3. Header from top: `0.2"` / Footer from bottom: `0.2"`
4. Click OK

### Line numbers
1. **Format → Document → Layout tab** (Mac) or **Layout → Line Numbers** (Windows)
2. Enable line numbers: **Continuous** or **Restart each page** (project standard: restart each page)
3. Count by: `1`
4. From text: `0.2"` (or "Auto" — Word will respect the gutter)
5. Font: Aptos (or Arial), 9pt, color `#BFBFBF` (75% grey)  
   *(Note: Word's line number font dialog is limited — you may need to set this via a macro if the default isn't close enough)*

---

## 6. Style Reference Card

| Style | Size | Weight | Spacing (before/after) | Border |
|---|---|---|---|---|
| H1 (Title) | 14pt | Bold | 6pt / 12pt | None |
| H2 (Section) | 14pt | Bold | 18pt / 9pt | 1.5pt top, 4pt gap |
| H3 (Sub-section) | 12pt | Bold Italic | 6pt / 6pt | None |
| H4 (Sub-sub) | 10pt | Bold | 6pt / 6pt | None |
| Normal (body) | 10pt | Regular | 6pt / 6pt | None |
| Body Text 2 (byline) | 9pt | Regular | 0pt / 0pt | None |
| Bullet L1 | 10pt | Regular | 6pt / 6pt | • at 0.1", text at 0.25" |
| Bullet L2 | 10pt | Regular | 6pt / 6pt | ○ at 0.25", text at 0.4" |
| Numbered L1 | 10pt | Regular | 6pt / 6pt | 1. at indent |
| Numbered L2 | 10pt | Regular | 6pt / 6pt | a. at indent |
| Numbered L3 | 10pt | Regular | 6pt / 6pt | i. at indent |

**Line spacing:** Multiple 1.1× throughout (all styles)  
**Font:** Aptos (fallback: Arial)  
**Page:** 8.5×11", margins 0.5" all sides, gutter 0.2", header/footer 0.2" from edge  
**Line numbers:** On, restart per page, 9pt, 75% grey (#BFBFBF)  
**Table headers:** Light grey fill (#D9D9D9), 10pt bold  
**Table cell padding:** ~0.04" top/bottom, ~0.07" left/right  

---

## 7. Status Cell Color Key (Dependency Chain Tables)

| Color | Hex | Meaning |
|---|---|---|
| Green | `#E2EFDA` | On track / Active / Ready |
| Yellow | `#FFF2CC` | Pending / At risk / TBD |
| Red | `#FCE4D6` | Blocked / Critical gap |
